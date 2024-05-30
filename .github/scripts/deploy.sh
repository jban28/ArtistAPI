funcs_to_deploy=($FUNCS_TO_DEPLOY)

for func in "${funs_to_deploy[@]}"
do
    file_path="src/${func}"
    zip -r -j lambda.zip $file_path
    echo $func
    func_name="ArtistAPI_${func}"
    echo $func_name
    aws lambda update-function-code --function-name="${func_name}" --zip-file=fileb://lambda.zip
done