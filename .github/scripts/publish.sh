funcs_to_deploy=($FUNCS_TO_DEPLOY)

for func in "${funcs_to_deploy[@]}"
do
    func_name="ArtistAPI_${func}"
    echo $func_name

    version=$(aws lambda publish-version --function-name="${func_name}" --query "Version")
    aws lambda update-alias --function-name "${func_name}" --name live --function-version "$version"
done