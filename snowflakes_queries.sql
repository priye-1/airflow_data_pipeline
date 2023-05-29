-- create database

CREATE DATABASE SNOWFLAKE_DATAPIPELINE_DB;
use schema snowflake_datapipeline_db.public;


-- create table
create or replace TABLE s3_dataset_table (
    ABOUT VARCHAR(16777216),
    ASSSOCIATED_LOC VARCHAR(16777216),
    ASSOCIATED_ORG VARCHAR(16777216),
    CATEGORY VARCHAR(16777216),
    DOB VARCHAR(16777216),
    IMAGE_URL VARCHAR(16777216),
    REWARD VARCHAR(16777216),
    TITLE VARCHAR(16777216),
    URL VARCHAR(16777216)
);


-- create stage
CREATE OR REPLACE STAGE snowflake_datapipeline_db.public.S3_dataset_stage
    URL = 's3://<s3 Bucket path>/'
    CREDENTIALS=(AWS_KEY_ID='<AWS KEY>' AWS_SECRET_KEY='<AWS SECRET>')
    FILE_FORMAT = (TYPE = 'CSV');


-- creating pipe                
CREATE OR REPLACE pipe snowflake_datapipeline_db.public.S3_dataset_pipe auto_ingest=true as   
    copy into snowflake_datapipeline_db.public.S3_dataset_table   
    from @snowflake_datapipeline_db.public.S3_dataset_stage
    FILE_FORMAT = (FIELD_DELIMITER = ',', SKIP_HEADER =1, TYPE = 'CSV', FIELD_OPTIONALLY_ENCLOSED_BY='"')
    ON_ERROR = 'CONTINUE';


-- check new pipe to copy ARN
show pipes;

-- check history for failed or successful copy operations in pipe
select * from table(information_schema.copy_history(TABLE_NAME=>'S3_dataset_table', START_TIME=> DATEADD(hours, -1, CURRENT_TIMESTAMP())));


