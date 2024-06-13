api_name="ArtistAPITest"
auth_uri=""
top_level_resources=("all-images" "login" "image" "image-data" "reorder")
declare -A top_level_ids

api_id=$(aws apigateway create-rest-api --name "$api_name" --query "id" --output "text")
root_resource_id=$(aws apigateway get-resources --rest-api-id "$api_id" --query "items[0].id"  --output "text")

# Authorizer
aws apigateway create-authorizer \
    --rest-api-id "$api_id" \
    --name "lambda_auth" \
    --type "TOKEN" \
    --authorizer-uri "$auth_uri"

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

aws apigateway create-resource \
    --rest-api-id "$api_id" \
    --parent-id "${top_level_ids[image]}" \
    --path-part "{id}" \

aws apigateway create-resource \
    --rest-api-id "$api_id" \
    --parent-id "${top_level_ids[image-data]}" \
    --path-part "{id}" \



# Create methods
# args: resource ID, http method, authorisation, function name, path
create_method() {
    aws apigateway put-method \
        --rest-api-id "$api_id" \
        --resource-id "$1" \
        --http-method "$2" \
        --authorization-type "$3"

    aws apigateway put-integration \
        --rest-api-id "$api_id" \
        --resource-id "$1" \
        --http-method "$2" \
        --type "AWS_PROXY" \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:053630928262:function:$4:\${stageVariables.stageName}/invocations"

    stages=("live" "dev")
    for stage in "${stages[@]}"; do
        aws lambda add-permission \
            --function-name "arn:aws:lambda:eu-west-2:053630928262:function:$4:${stage}" \
            --source-arn "arn:aws:execute-api:eu-west-2:053630928262:bngqwa0zb2/*/$2/$5" \
            --principal apigateway.amazonaws.com \
            --statement-id Allow-API_Invoke-Access \
            --action lambda:InvokeFunction
    done
}

create_method "${top_level_ids[all-images]}" "GET" "NONE" "ArtistAPI_all-images-by-series" "all-images"
