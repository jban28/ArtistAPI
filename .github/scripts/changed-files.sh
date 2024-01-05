func_files+=($(ls lambda-functions/*.py))

for file in "${func_files[@]}"
do
    if [[ ${ALL_CHANGED_FILES[@]} =~ $file ]]
    then
        changed_func_files+=($file)
    fi
done

echo "${#changed_func_files[@]}"

echo "files_to_deploy=${changed_func_files[@]}" >> $GITHUB_OUTPUT
echo "changes=${#changed_func_files[@]}" >> $GITHUB_OUTPUT