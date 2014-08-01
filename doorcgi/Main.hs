{-# LANGUAGE EmptyDataDecls    #-}
{-# LANGUAGE FlexibleContexts  #-}
{-# LANGUAGE GADTs             #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes       #-}
{-# LANGUAGE TemplateHaskell   #-}
{-# LANGUAGE TypeFamilies      #-}

import Control.Monad.IO.Class (liftIO)
import Control.Monad.Trans.Resource (runResourceT, ResourceT)
import Database.Persist
import Database.Persist.MySQL
import Database.Persist.TH
import Data.Configurator
import Data.Configurator.Types
import Data.Text (Text)
import Data.Time (UTCTime, getCurrentTime)
import qualified Web.Scotty as S

-- | id          | int(11)      | NO   | PRI | NULL              | auto_increment |
-- | occurred_at | timestamp    | NO   |     | CURRENT_TIMESTAMP |                |
-- | name        | varchar(255) | YES  |     | NULL              |                |
share [mkPersist sqlSettings, mkMigrate "migrateAll"] [persistLowerCase|
Entries
    occurredAt UTCTime
    name Text
    deriving Show
|]

runDb :: SqlPersist (ResourceT IO) a -> ConnectInfo -> IO a
runDb query ci = runResourceT . withMySQLConn ci . runSqlConn $ query

getConfig :: IO Config
getConfig = load [Required "/etc/doorcgi.conf"]

main = do
  config <- liftIO getConfig
  runDb (runMigration migrateAll) -- TODO
  S.scotty 3000 $ do
    S.get "/create/:title" $ do
      _title <- S.param "title"
      now <- liftIO getCurrentTime
      --liftIO $ runDb $ insert $ Post _title "some content" now
      S.redirect "/"
