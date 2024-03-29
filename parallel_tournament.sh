#!/bin/bash
echo "Start Tournament"
source venv/bin/activate

script1=chriweb_A1
script2=greedy_player
#script2=simbach_A1
#script2=mlapae_A1
#script2=iana_player5
#script2=pduegg_A1
player1=IntrepidIbex
player2=GreedyPlayer
#player2=TouchMyTralala
#player2=Bublik
#player2=Barash
#player2=AwesomeAgent

n_maps=20

ts=$(date "+%Y%m%d%H%M%S")


log_name=$(echo tournament/${ts}/log/tournament_result.log)
log_name_rev=$(echo tournament/${ts}/log/tournament_result_rev.log)

mkdir tournament/${ts}
mkdir tournament/${ts}/log
mkdir tournament/${ts}/maps

for i in $(seq -w 001 $n_maps);
do
   python map_generator.py -n "tournament/${ts}/maps/tournament_${i}"
done

for i in $(seq -w 001 $n_maps);
do
    python kingsheep_tournament.py tournament/${ts}/maps/tournament_${i}.map -p1m $script1 -p1n $player1 -p2m $script2 -p2n $player2 >> "$log_name" &
    python kingsheep_tournament.py tournament/${ts}/maps/tournament_${i}.map -p1m $script2 -p1n $player2 -p2m $script1 -p2n $player1 >> "$log_name_rev" &
done

deactivate

echo "End Tournament"