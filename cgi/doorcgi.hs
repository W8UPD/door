{-# LANGUAGE OverloadedStrings #-}
import Control.Monad
import Control.Monad.IO.Class
import Data.Char (chr)
import Data.Configurator
import Data.Configurator.Types
import Data.Maybe (fromMaybe)
import Database.HDBC
import Database.HDBC.MySQL
import Network.CGI (CGI, CGIResult, authType, getInput, remoteAddr, output, runCGI, handleErrors)
import Network.Socket

getConfig :: IO Config
getConfig = load [Required "/etc/doorcgi.conf"]

passwordCheck :: Maybe String -> Maybe String -> Bool
passwordCheck (Just x) (Just y) = x == y
passwordCheck _ _ = False

reportToIrc :: Maybe String -> Maybe Integer -> String -> IO ()
reportToIrc Nothing _ _ = return ()
reportToIrc _ Nothing _ = return ()
reportToIrc (Just host) (Just port) name = withSocketsDo $ do
  s <- socket AF_INET Datagram defaultProtocol
  host' <- inet_addr host
  sendTo s ("The shack door was unlocked by " ++ [chr 2] ++ name ++ [chr 2] ++ ".") (SockAddrInet (PortNum (fromInteger port)) host')
  return ()

cgiMain :: CGI CGIResult
cgiMain = do
  config <- liftIO getConfig
  configPassword <- liftIO $ Data.Configurator.lookup config "password"
  givenPassword <- getInput "password"
  givenName <- getInput "name"

  dbUser <- liftIO $ Data.Configurator.lookup config "db_user"
  dbPass <- liftIO $ Data.Configurator.lookup config "db_pass"
  dbName <- liftIO $ Data.Configurator.lookup config "db_name"
  udpHost <- liftIO $ Data.Configurator.lookup config "udp_host"
  udpPort <- liftIO $ Data.Configurator.lookup config "udp_port"

  if passwordCheck configPassword givenPassword
    then do
      conn <- liftIO $ connectMySQL defaultMySQLConnectInfo {
        mysqlUser = fromMaybe "" dbUser,
        mysqlPassword = fromMaybe "" dbPass,
        mysqlDatabase = fromMaybe "" dbName }
      stmt <- liftIO $ prepare conn "INSERT INTO entries(name) VALUES(?)"
      liftIO $ execute stmt [SqlString $ fromMaybe "<Unknown Name>" givenName]
      liftIO $ reportToIrc udpHost udpPort (fromMaybe "<Unknown Name>" givenName)
      output "You've authed!"
    else output "Auth failed!"

main :: IO ()
main = runCGI (handleErrors cgiMain)
