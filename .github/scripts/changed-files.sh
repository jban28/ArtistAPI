func_files+=($(ls lambda-functions/*.py))
changed_func_files=()

for file in "${func_files[@]}"
do
    if [[ ${ALL_CHANGED_FILES[@]} =~ $file ]]
    then
        changed_func_files+=($file)
    fi
done

num="${#changed_func_files[@]}"
echo $changed_func_files

echo "files_to_deploy=${changed_func_files[@]}" >> $GITHUB_OUTPUT
echo "changes=${num}" >> $GITHUB_OUTPUT