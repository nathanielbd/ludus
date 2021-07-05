#!env sh

status=0

message() {
    echo ""
    echo "$1"
    echo "--------------------------------------------------------------------------------"
    echo ""
}

emessage() {
    message "$1" >&2
}

run_with_log() {
    program="$1"
    args="$2"
    logfile="${program}.log"
    cmd="${program} ${args}"

    message "running ${cmd}"
    
    if ${cmd} 2>&1 | tee ${logfile}; then
        rm ${logfile}
    else
        status=$?
        exho
        emessage "${cmd} failed with code ${status}. see ${logfile} for details"
    fi
}

run_with_log mypy
run_with_log pytest "--log-level info"
run_with_log flake8 --count

if [ ${status} -ne 0 ]; then
    emessage "something failed! please fix it before committing"
else
    message "looks good! go ahead and commit"
fi

exit ${status}
