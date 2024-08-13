# JWA-datamine

## Prerequisites
**On PC:**<br>
- Python 3 to run scripts. (And some modules, could be installed by pip). <br>
- Apktool to unpack APK file.<br>
- AssetStudio to unpack assets (creature pictures).<br>

**On phone:**<br>
- PCAPdroid to capture traffic.<br>
- (Optional) PCAPdroid-mitm to get player names (ROOT).

## Core files
**MyParser.py** - Protocol parser. Thanks to Lullatsch.<br>
**utilities.py** - Environment file. Included in almost all other files.<br>
**unpcap.py** - Unpacks pcap file.

## Main processing
**SplitConversation.py** - Data analyzer. Unpacks the pcap file and performs a preliminary analysis.<br>
**Parse_APK.py** - Parses new APK file. Only calls some other scripts, may be done manually.<br>
**analize_encryption.py** - Parses changes between versions (unpacks com.ludia.jw2\cache\OnlineOptionCache).

## Analysis helpers
**generate_map.py** - Generates file with links between files.<br>
**Creaturedex.py** - Generates file with current creature list and moves. Can be used for other things.<br>
**compare.py** - Helper to find some real changes between versions. Ignores small changes (such as added empty sections).

## Game data
**Campaign.py** - Campaign rewards table.<br>
**omega_stat.py** - Omega stats table.

## Infographics
**Collage.py** - Weekly calendar.<br>
**Isla.py** - Current Isla event.<br>
**Pass.py** - Current battle pass rewards.<br>
**RewardList.py** - Custom list (such as login calendar).<br>
**tour_creatures.py** - Creatures with some move restrictions.<br>
**Brawl_creatures.py** - Creatures elegible for current brawl.<br>
**Discount.py** - Creatures elegible for discount event.<br>
**zones.py** - Current spawn distribution.<br>
**Top-30-example.py** - Draws tournament statistics. (You need do click on all players in rankings).

## Personal statistics
**DartRecords.py** - Darting records.<br>
**Hardcap.py** - Shows all DNA counts.<br>
**fill_gtable.py** - Creature list with DNA (for external use).

## Player statistics
(You need to click on players you want to analyze)<br>
**acc_stats.py** - Some account metrics.<br>
**alliance_digest.py** - Creatures stats.<br>
**XP.py** - Players' XP.<br>
**Boosts.py** - Players' boosts.

## Alliance stuff
**alliance_stats.py** - Alliance tournament and weekly results.<br>
**HoF.py**, **HoF2.py**, **HoF_total.py** - Infographics for tournament results (for alliance family).<br>
**sanc_time.py** - Helper for sanctuary management.

## Minor researches
**moves_count.py** - Number of moves per creature.<br>
**attack_timing.py** - Longest and shortest attacks.

## Other
**find_banned.py** - Compares tournament results to find deleted entries.<br>
**parse_nicknames.py** - Gets player nicknames from mitm capture (needs root!).<br>
**img_cutter.py** - make stickers for Telegram.<br>
**transparency_fix.py** - Helper for img_cutter.
