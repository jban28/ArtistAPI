lambda_funcs=($(ls src/lambda_functions/*.py))

for func_file in "${lambda_funcs[@]}"; do
    func_name="${func_file/.py/}"
    func_name="ArtistAPI_${func_name##*/}"

    version=$(aws lambda publish-version --function-name="${func_name}" --query "Version")

    version=${version//\"/}
    aws lambda update-alias --function-name "${func_name}" --name "live" --function-version $version
done