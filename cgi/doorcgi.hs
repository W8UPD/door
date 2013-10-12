{-# LANGUAGE OverloadedStrings #-}
import Control.Monad
import Control.Monad.IO.Class
import Data.Configurator
import Data.Configurator.Types
import Data.Maybe (fromMaybe)
import Database.HDBC
import Database.HDBC.MySQL
import Network.CGI (CGI, CGIResult, authType, getInput, remoteAddr, output, runCGI, handleErrors)

getConfig :: IO Config
getConfig = load [Required "/etc/doorcgi.conf"]

passwordCheck :: Maybe String -> Maybe String -> Bool
passwordCheck (Just x) (Just y) = x == y
passwordCheck _ _ = False

cgiMain :: CGI CGIResult
cgiMain = do
  config <- liftIO getConfig
  configPassword <- liftIO $ Data.Configurator.lookup config "password"
  givenPassword <- getInput "password"
  givenName <- getInput "name"

  dbUser <- liftIO $ Data.Configurator.lookup config "db_user"
  dbPass <- liftIO $ Data.Configurator.lookup config "db_pass"
  dbName <- liftIO $ Data.Configurator.lookup config "db_name"

  if passwordCheck configPassword givenPassword
    then do
      conn <- liftIO $ connectMySQL defaultMySQLConnectInfo {
        mysqlUser = fromMaybe "" dbUser,
        mysqlPassword = fromMaybe "" dbPass,
        mysqlDatabase = fromMaybe "" dbName
      }
      stmt <- liftIO $ prepare conn "INSERT INTO entries(name) VALUES(?)"
      liftIO $ execute stmt [SqlString $ fromMaybe "<Unknown Name>" givenName]
      output "You've authed!"
    else output "Auth failed!"

main :: IO ()
main = runCGI (handleErrors cgiMain)
