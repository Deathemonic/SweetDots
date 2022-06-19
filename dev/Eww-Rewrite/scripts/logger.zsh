#!/usr/bin/env zsh

cache="$HOME/.cache/ewwsideboard"
logs="$cache/notifications.txt"
empty_quote_cache="$cache/quotes.txt"
empty_quote="No notifications"

unset_vars () {
  unset cache
  unset logs
  unset empty_quote_cache
  unset empty_quote
}

mkdir $cache 2>/dev/null
touch $logs 2>/dev/null

create_cache () {
  local urgency
  
  case "$notify_urgency" in
    "LOW"|"NORMAL"|"CRITICAL") 
      urgency="$notify_urgency"
    ;;
    *) 
      urgency="OTHER"
    ;;
  esac

  local summary
  local body

  [ "$notify_summary" = "" ] && summary="Summary unavailable." || summary="$notify_summary"
  [ "$notify_body" = "" ] && body="Body unavailable." || body="$(print "$notify_body" | recode html)"

  local glyph

  case "$urgency" in
    "LOW") 
      glyph="L"
    ;;
    "NORMAL") 
      glyph="N"
    ;;
    "CRITICAL") 
      glyph="C"
    ;;
    *) 
      glyph="O"
    ;;
  esac

  case "$app_name" in
    "spotify") 
      glyph="S"
    ;;
    "mpd") 
      glyph="M"
    ;;
    "brightness") 
      glyph="B"
    ;;
    "nightmode") 
      glyph="N"
    ;;
    "microphone") 
      glyph="P"
    ;;
    "volume") 
      glyph="V"
    ;;
    "screenshot") 
      glyph="C"
    ;;
    "firefox")
      glyph="F"
    ;;
  esac

  # pipe stdout -> pipe cat stdin (cat conCATs multiple files and sends to stdout) -> absorb stdout from cat
  # concat: "one" + "two" + "three" -> notice how the order matters i.e. "one" will be prepended
  print '(card :class "sideboard-card sideboard-card-'$urgency' sideboard-card-'$app_name'" :glyph_class "sideboard-'$urgency' sideboard-'$app_name'" :SL "'$DUNST_ID'" :L "dunstctl history-pop '$DUNST_ID'" :body "'$body'" :summary "'$summary'" :glyph "'$glyph'")' \
    | cat - "$logs" \
    | sponge "$logs"
}

compile_caches () {
  tr '\n' ' ' < "$logs" 
}

make_literal () {
  local caches="$(compile_caches)"
  local quote="$($HOME/Documents/Eww/scripts/quotes notify_empty_rand)"

  [[ "$caches" == "" ]] \
    && print '(box :class "sideboard-empty-box" :height 750 :orientation "vertical" :space-evenly false (image :class "sideboard-empty-banner" :valign "end" :vexpand true :path "./assets/clock.png" :image-width 200 :image-height 200) (label :vexpand true :valign "start" :wrap true :class "sideboard-empty-label" :text "'$quote'"))' \
    || print "(scroll :height 750 :vscroll true (box :orientation 'vertical' :class 'sideboard-scroll-box' :spacing 10 :space-evenly false $caches))"
}

clear_logs () {
  killall dunst 2>/dev/null
  dunst & disown
  print > "$logs"
}

pop () {
  sed -i '1d' "$logs" 
}

drop() {
  sed -i '$d' "$logs" 
}

remove_line () {
  sed -i '/SL "'$1'"/d' "$logs" 
}

critical_count () { 
  local crits=$(cat $logs | grep CRITICAL | wc --lines)
  local total=$(cat $logs | wc --lines)

  print $(((crits*100)/total))
}

normal_count () { 
  local norms=$(cat $logs | grep NORMAL | wc --lines)
  local total=$(cat $logs | wc --lines)

  print $(((norms*100)/total))
}

low_count () { 
  local lows=$(cat $logs | grep LOW | wc --lines)
  local total=$(cat $logs | wc --lines)

  print $(((lows*100)/total))
}

subscribe () {
  make_literal

  local lines=$(cat $logs | wc -l)

  while sleep 0.1; do
    local new=$(cat $logs | wc -l)
    [[ $lines -ne $new ]] && lines=$new && print
  done | while read -r _ do; make_literal done
}

case "$1" in
  pop) 
    pop
  ;;
  drop) 
    drop
  ;;
  clear) 
    clear_logs
  ;;
  subscribe) 
    subscribe
  ;;
  rm_id) 
    remove_line $2
  ;;
  crits) 
    critical_count
  ;;
  lows) 
    low_count
  ;;
  norms) 
    normal_count
  ;;
  *) 
    create_cache
  ;;
esac

sed -i '/^$/d' "$logs"
unset_vars