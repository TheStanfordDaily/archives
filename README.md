# Stanford Daily archives

## Setup
```
yum install GraphicsMagick ImageMagick
```

`list_metadata.js` lists metadata in tsd archive s3 bucket and puts them in metadata.json.

`upload-search.js` - takes and parses xml files, then puts them into Azure Search.


aws lambda add-permission --profile tsd --function-name archives-resizer --principal s3.amazonaws.com --statement-id id1 --action "lambda:InvokeFunction" --source-arn arn:aws:s3:::stanforddailyarchive-source --source-account 607998788272

~ $aws lambda get-policy --function-name archives-resizer --profile tsd
{
    "Policy": "{\"Version\":\"2012-10-17\",\"Id\":\"default\",\"Statement\":[{\"Sid\":\"id1\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"s3.amazonaws.com\"},\"Action\":\"lambda:InvokeFunction\",\"Resource\":\"arn:aws:lambda:us-east-1:607998788272:function:archives-resizer\",\"Condition\":{\"StringEquals\":{\"AWS:SourceAccount\":\"607998788272\"},\"ArnLike\":{\"AWS:SourceArn\":\"arn:aws:s3:::stanforddailyarchive-source\"}}}]}",
    "RevisionId": "d5c99623-ee01-4126-ba8b-a248aeaad095"
}

sudo yum install libjpeg-turbo8-dev libfreetype6-dev zlib1g-dev \
liblcms2-dev liblcms2-utils libtiff5-dev python-dev libwebp-dev apache2 \
libapache2-mod-wsgi