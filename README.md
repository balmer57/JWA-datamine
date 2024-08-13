# JWA-datamine

## Core files
**MyParser.py** - Protocol parser. Thanks to Lullatsch.
**utilities.py** - Environment file. Included in almost all other files.
**unpcap.py** - Unpacks pcap file. 

## Main processing
**SplitConversation.py** - Data analyzer. Unpacks the pcap file and performs a preliminary analysis.
**Parse_APK.py** - Parses new APK file. Only calls some other scripts, may be done manually.
**analize_encryption.py** - Parses changes between versions (unpacks com.ludia.jw2\cache\OnlineOptionCache).

## Analysis helpers
**generate_map.py** - Generates file with links between files.
**Creaturedex.py** - Generates file with current creature list and moves. Can be used for other things.
**compare.py** - Helper to find some real changes between versions. Ignores small changes (such as added empty sections).

## Game data
**Campaign.py** - Campaign rewards table.
**omega_stat.py** - Omega stats table.

## Infographics
**Collage.py** - Weekly calendar.
**Isla.py** - Current Isla event.
**Pass.py** - Current battle pass rewards.
**RewardList.py** - Custom list (such as login calendar).
**tour_creatures.py** - Creatures with some move restrictions.
**Brawl_creatures.py** - Creatures elegible for current brawl.
**Discount.py** - Creatures elegible for discount event.
**zones.py** - Current spawn distribution.
**Top-30-example.py** - Draws tournament statistics. (You need do click on all players in rankings).

## Personal statistics
**DartRecords.py** - Darting records.
**Hardcap.py** - Shows all DNA counts.
**fill_gtable.py** - Creature list with DNA (for external use).

## Player statistics
(You need to click on players you want to analyze)
**acc_stats.py** - Some account metrics.
**alliance_digest.py** - Creatures stats.
**XP.py** - Players' XP.
**Boosts.py** - Players' boosts.

## Alliance stuff
**alliance_stats.py** - Alliance tournament and weekly results.
**HoF.py**, **HoF2.py**, **HoF_total.py** - Infographics for tournament results (for alliance family).
**sanc_time.py** - Helper for sanctuary management.

## Minor researches
**moves_count.py** - Number of moves per creature.
**attack_timing.py** - Longest and shortest attacks.

## Other
**find_banned.py** - Compares tournament results to find deleted entries.
**parse_nicknames.py** - Gets player nicknames from mitm capture (needs root!).
**img_cutter.py** - make stickers for Telegram.
**transparency_fix.py** - Helper for img_cutter.
