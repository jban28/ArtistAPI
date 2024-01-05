for file in "${FILES_TO_DEPLOY[@]}"
do
    zip -j lambda.zip $file
    str="${file%.py}"
    func_name="ArtistAPI_${str##*/}"
    echo $func_name
    aws lambda update-function-code --function-name=ArtistAPI_"${func_name}" --zip-file=fileb://lambda.zip
done