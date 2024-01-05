FILES_TO_DEPLOY=("lambda-functions/login.py")

for file in "${FILES_TO_DEPLOY[@]}"
do
    zip -j lambda.zip $file
    str="${file%.py}"
    func_name="ArtistAPI_${str#*/}"
    aws lambda update-function-code --function-name=ArtistAPI_"${file%.py}" --zip-file=fileb://lambdaAPI.zip
done