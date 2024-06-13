# API design and structure

## Public Endpoints
GET /all-images             return all images for given artist, allowing for returning unsorted or by series with a header defining the sorting mechanism (if any)
POST /login                 allows users to login

## Authenticated Endpoints (artist must be logged in and request made with valid token)
PUT /image/{filename}       upload new image to S3 bucket
POST /image-data            add data about new image to database
DELETE /image/{id}          delete an image from the S3 bucket and the database
PUT /image-data/{id}        database entry for an image (not the image itself)
PUT /reorder                update database entries to reorder images in a series

## Corresponding Lambda Functions/API Gateway endpoints with proxy integration
/all-images                 GET
/login                      POST
/image-data                 POST
/image-data/{id}            PUT
/image/{id}                 DELETE, PUT
/reorder                    PUT