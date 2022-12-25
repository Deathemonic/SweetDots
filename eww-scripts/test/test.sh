cpu_value () {
    preview_total=0
    preview_idle=0
    cache="/tmp/cpu_value.cache.eww"


    if [[ -f "${cache}" ]]; then
		file=$(cat "${cache}")
		preview_total=$(echo "${file}" | head -n 1)
		preview_idle=$(echo "${file}" | tail -n 1)
	fi

	cpu=(`cat /proc/stat | grep '^cpu '`)
	unset cpu[0]
	idle=${cpu[4]}

	total=0

	for value in "${cpu[@]:0:4}"; do
		let "total=$total+$value"
	done

	if [[ "${preview_total}" != "" ]] && [[ "${preview_idle}" != "" ]]; then
		let "diff_idle=$idle-$preview_idle"
		let "diff_total=$total-$preview_total"
		let "diff_usage=(1000*($diff_total-$diff_idle)/$diff_total+5)/10"
		echo "${diff_usage}"
	else
		echo "0"
	fi

	echo "${total}" > "${cache}"
	echo "${idle}" >> "${cache}"
}

cpu_value