{-# LANGUAGE EmptyDataDecls    #-}
{-# LANGUAGE FlexibleContexts  #-}
{-# LANGUAGE GADTs             #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes       #-}
{-# LANGUAGE TemplateHaskell   #-}
{-# LANGUAGE TypeFamilies      #-}

import Control.Monad (unless)
import Control.Monad.IO.Class (liftIO)
import Control.Monad.Logger
import Control.Monad.Trans.Resource (runResourceT, ResourceT)
import Data.Char (chr)
import Data.Configurator
import Data.Configurator.Types
import Data.Monoid ((<>))
import Data.Text (Text, unpack)
import Data.Time (UTCTime, getCurrentTime)
import Database.Persist
import Database.Persist.MySQL
import Database.Persist.TH
import Network.HTTP.Types.Status
import Network.Socket
import qualified Web.Scotty as S

share [mkPersist sqlSettings, mkMigrate "migrateAll"] [persistLowerCase|
Entries
  occurredAt UTCTime
  name Text
  hidden Bool
  deriving Show
DoorStates
  occurredAt UTCTime
  state Text
  deriving Show
AlarmEvent
  occurredAt UTCTime
  deriving Show
|]

runDb :: ConnectInfo -> SqlPersistT (ResourceT (NoLoggingT IO)) a -> IO a
runDb ci query = runNoLoggingT .
                 runResourceT .
                 withMySQLConn ci .
                 runSqlConn $ query

reportToIRC :: String -> Integer -> String -> IO ()
reportToIRC host port msg = withSocketsDo $ do
  s <- socket AF_INET Datagram defaultProtocol
  host' <- inet_addr host
  _ <- sendTo s msg (SockAddrInet (fromIntegral port) host')
  return ()

getConfig :: IO Config
getConfig = load [Required "/etc/doorcgi.conf"]

main :: IO ()
main = do
  config <- liftIO getConfig
  configPassword <- liftIO $ require config "password" :: IO Text
  dbUser <- liftIO $ require config "db_user"
  dbPass <- liftIO $ require config "db_pass"
  dbName <- liftIO $ require config "db_name"
  udpHost <- liftIO $ require config "udp_host" :: IO String
  udpPort <- liftIO $ require config "udp_port"

  let dbConfig =
        defaultConnectInfo {
          connectUser     = dbUser
        , connectPassword = dbPass
        , connectDatabase = dbName
        }
  let irc msg = liftIO $ reportToIRC udpHost udpPort msg

  runDb dbConfig (runMigration migrateAll)
  S.scotty 3000 $ do
    S.get "/" $ do
      password <- S.param "password"

      unless (password == configPassword) $ do
        S.status status403
        S.raise "Invalid password"

      event <- S.param "event"
      now <- liftIO getCurrentTime
      case event :: Text of
        "auth_success" -> do
          name <- S.param "name"
          _ <- liftIO $ runDb dbConfig $ insert (Entries now name False)
          irc $ "The shack door was " <> [chr 3] <> "3unlocked " <> [chr 3] <> "by " <> [chr 2] <> unpack name <> [chr 2] <> "."
          S.text "Success"
        "door_opened" -> do
          _ <- liftIO $ runDb dbConfig $ insert (DoorStates now "opened")
          irc $ "The shack door was " <> [chr 3] <> "7opened" <> [chr 3] <> "."
          S.text "Success"
        "door_closed" -> do
          _ <- liftIO $ runDb dbConfig $ insert (DoorStates now "closed")
          irc $ "The shack door was " <> [chr 3] <> "5closed" <> [chr 3] <> "."
          S.text "Success"
        "alarm_triggered" -> do
          _ <- liftIO $ runDb dbConfig $ insert (DoorStates now "closed")
          irc $ "The shack door alarm was " <> [chr 3] <> "4triggered" <> [chr 3] <> "."
          S.text "Success"
        _ -> S.text "Unknown event."
