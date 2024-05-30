func_folders+=($(ls src/functions/))
changed_funcs=()

for folder in "${func_folders[@]}"
do
    func_files=($(ls src/functions/$folder/*.py))
    for file in "${func_files[@]}"
    do
        if [[ ${ALL_CHANGED_FILES[@]} =~ $file ]]
        then
            echo $folder
            changed_funcs+=($folder)
        fi
    done
done

num="${#changed_funcs[@]}"
echo $changed_funcs
echo ${changed_funcs[@]}


echo "funcs_to_deploy=${changed_funcs[@]}" >> $GITHUB_OUTPUT
echo "changes=${num}" >> $GITHUB_OUTPUT