func_files+=($(ls lambda-functions/*.py))
changed_func_files=()

for file in "${func_files[@]}"
do
    if [[ ${ALL_CHANGED_FILES[@]} =~ $file ]]
    then
        changed_func_files+=($file)
    fi
done

num="changes=${#changed_func_files[@]}"
echo $num

echo files_to_deploy=${changed_func_files[@]} >> $GITHUB_OUTPUT
echo "${num}" >> $GITHUB_OUTPUT