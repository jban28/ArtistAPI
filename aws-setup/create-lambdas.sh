lambda_funcs=($(ls src/lambda_functions/*.py))
layer_arn="arn:aws:lambda:eu-west-2:053630928262:layer:ArtistAPI_base:16"

for func_file in "${lambda_funcs[@]}"; do
    func_name="${func_file/.py/}"
    echo $func_name

    aws iam create-role \
        --role-name "$func_name\_lambda-role" \
        --assume-role-policy-document "aws-setup/role.json"

    zip lambda.zip $func_file

    aws lambda create-function \
    --function-name "$func_name" \
    --runtime "python3.10" \
    --role "arn:aws:iam::053630928262:role/${func_name}_lambda-role" \
    --zip-file "fileb://lambda_function.zip" \
    --handler "${func_name}.lambda_handler" \
    --layers "$layer_arn" \
    --environment `VARIABLES="{databaseURI=$DATABASE_URI,rootURL=https://artist-api.s3.amazonaws.com}"` 

    aws lambda create-alias \
    --function-name "$func_name" \
    --name "live" \
    --function-version "\$LATEST"

    aws lambda create-alias \
    --function-name "$func_name" \
    --name "dev" \
    --function-version "\$LATEST" 
done

aws lambda update-function-configuration \
    --function-name ArtistAPI_auth \
    --environment `VARIABLES="{databaseURI=$DATABASE_URI,rootURL=https://artist-api.s3.amazonaws.com,secretKey=$SECRET_KEY}"`

aws lambda update-function-configuration \
    --function-name ArtistAPI_login_POST \
    --environment `VARIABLES="{databaseURI=$DATABASE_URI,rootURL=https://artist-api.s3.amazonaws.com,secretKey=$SECRET_KEY}"`