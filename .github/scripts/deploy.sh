for func in "${FUNCS_TO_DEPLOY[@]}"
do
    zip -j lambda.zip $func
    echo $func
    func_name="ArtistAPI_${func}"
    echo $func_name
    aws lambda update-function-code --function-name="${func_name}" --zip-file=fileb://lambda.zip
done