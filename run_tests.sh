#!env sh

status=0

message() {
    echo ""
    echo "$1"
    echo ""
}

emessage() {
    message "$1" >&2
}

run_with_log() {
    cmd="$1"
    logfile="${cmd}.log"
    if ${cmd} 2>&1 | tee ${logfile}; then
        rm ${logfile}
    else
        status=$?
        exho
        emessage "${cmd} failed with code ${status}. see ${logfile} for details"
    fi
}

run_with_log mypy
run_with_log pytest
run_with_log flake8

if [ ${status} -ne 0 ]; then
    emessage "something failed! please fix it before committing"
else
    message "looks good! go ahead and commit"
fi

exit ${status}
