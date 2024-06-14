funcs_to_deploy=($FUNCS_TO_DEPLOY)

for func in "${funcs_to_deploy[@]}"
do
    file_path="src/lambda_functions/${func}.py"
    zip -j lambda.zip $file_path
    func_name="ArtistAPI_${func}"
    aws lambda update-function-code --function-name="${func_name}" --zip-file=fileb://lambda.zip
done
