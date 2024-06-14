api_name="ArtistAPI"
auth_uri="arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:053630928262:function:$api_name\_auth:\${stageVariables.stageName}/invocations"
top_level_resources=("all-images-by-series" "login" "image" "image-data" "reorder")
declare -A top_level_ids

api_id=$(aws apigateway create-rest-api --name "$api_name" --query "id" --output "text")
root_resource_id=$(aws apigateway get-resources --rest-api-id "$api_id" --query "items[0].id"  --output "text")

# Authorizer
auth_id=$(aws apigateway create-authorizer \
    --rest-api-id "$api_id" \
    --name "lambda_auth" \
    --type "TOKEN" \
    --authorizer-uri "$auth_uri" \
    --query "id"
)

# Resources
for resource_name in "${top_level_resources[@]}"; do
    top_level_ids["$resource_name"]=$(aws apigateway create-resource \
        --rest-api-id "$api_id" \
        --parent-id "$root_resource_id" \
        --path-part "$resource_name" \
        --query "id" \
        --output "text"
    )
done

image_id_res_id=$(aws apigateway create-resource \
    --rest-api-id "$api_id" \
    --parent-id "${top_level_ids[image]}" \
    --path-part "{id}" \
    --query "id"
)

image_id_data_res_id=$(aws apigateway create-resource \
    --rest-api-id "$api_id" \
    --parent-id "${top_level_ids[image-data]}" \
    --path-part "{id}" \
    --query "id"
)


# Create methods
# args: api path, http method, authorisation, resource id, func name
create_method() {
    if [[ $4 == "NONE" ]]; then
        aws apigateway put-method \
            --rest-api-id "$api_id" \
            --resource-id "$4" \
            --http-method "$2" \
            --authorization-type "$3"
    else
        aws apigateway put-method \
            --rest-api-id "$api_id" \
            --resource-id "$4" \
            --http-method "$2" \
            --authorization-type "$3" \
            --authorizer-id "$auth_id"
    fi

    aws apigateway put-integration \
        --rest-api-id "$api_id" \
        --resource-id "$4" \
        --http-method "$2" \
        --type "AWS_PROXY" \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:053630928262:function:$api_name_$1:\${stageVariables.stageName}/invocations"

    stages=("live" "dev")
    for stage in "${stages[@]}"; do
        aws lambda add-permission \
            --function-name "arn:aws:lambda:eu-west-2:053630928262:function:$api_name_$1:${stage}" \
            --source-arn "arn:aws:execute-api:eu-west-2:053630928262:bngqwa0zb2/*/$2/$1" \
            --principal apigateway.amazonaws.com \
            --statement-id Allow-API_Invoke-Access \
            --action lambda:InvokeFunction
    done
}

create_method "all-images-by-series" "GET" "NONE" "${top_level_ids["all-images-by-series"]}" "ArtistAPI_all-images_GET"
create_method "login" "POST" "NONE" "${top_level_ids["login"]}" "ArtistAPI_login_POST"
create_method "image-data" "POST" "CUSTOM" "${top_level_ids["image-data"]}" "ArtistAPI_image-data_POST"
create_method "reorder" "PUT" "CUSTOM" "${top_level_ids["reorder"]}" "ArtistAPI_reorder_PUT"
create_method "{id}" "PUT" "CUSTOM" "${image_id_res_id}" "ArtistAPI_image_id_PUT"
create_method "{id}" "DELETE" "CUSTOM" "${image_id_res_id}" "ArtistAPI_image_id_DELETE"
create_method "{id}" "PUT" "CUSTOM" "${image_data_id_res_id}" "ArtistAPI_image-data_id_PUT"


aws apigateway create-deployment \
    --rest-api-id "$api_id" \
    --stage-name "live" \
    --variables "stageName=live" 
    
aws apigateway create-deployment \
    --rest-api-id "$api_id" \
    --stage-name "dev" \
    --variables "stageName=dev"