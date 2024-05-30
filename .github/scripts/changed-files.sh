func_folders+=($(ls src/))
changed_func_files=()

for folder in "${func_folders[@]}"
do
    func_files=($(ls src/$folder/*.py))
    for file in "${func_files[@]}"
    do
        if [[ ${ALL_CHANGED_FILES[@]} =~ $file ]]
        then
            changed_funcs+=($folder)
        fi
    done
done

num="${#changed_funcs[@]}"
echo $changed_funcs

echo "funcs_to_deploy=${changed_funcs[@]}" >> $GITHUB_OUTPUT
echo "changes=${num}" >> $GITHUB_OUTPUT