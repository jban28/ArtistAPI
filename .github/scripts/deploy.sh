for func in "${FUNCS_TO_DEPLOY[@]}"
do
    file_path="src/${func}"
    zip -j lambda.zip $file_path
    echo $func
    func_name="ArtistAPI_${func}"
    echo $func_name
    aws lambda update-function-code --function-name="${func_name}" --zip-file=fileb://lambda.zip
done