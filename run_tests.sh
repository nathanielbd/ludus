#!env sh

status=0
failures=""

errecho() {
    echo "$1" >&2
}

run_with_log() {
    program="$1"
    args="$2"
    logfile="${program}.log"
    cmd="${program} ${args}"

    echo ""
    echo "running ${cmd}"

    ${cmd} 2>&1 > ${logfile}
    res=$?
    
    if [ ${res} -eq 0 ]; then
        rm ${logfile}
    else
        status=${res}
        errecho "${cmd} failed with code ${status}. see ${logfile} for details"
        failures="${program} ${failures}"
        errecho ""
        errecho "${logfile}:"
        errecho "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        cat "${logfile}" >&2
        errecho "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    fi
}

run_with_log mypy
run_with_log pytest "--log-level info"
run_with_log flake8

if [ ${status} -ne 0 ]; then
    errecho "${failures}failed! please fix before committing"
else
    echo "looks good! go ahead and commit"
fi

exit ${status}
