# aSend (Cal Hacks 2019)

Crowdsourced Record Compiler powered by Blockchain


Imagine breaking world records from the comfort of your home. Never had a chance to showcase your special skills and talents? Now, you can with aSend! aSend is a crowdsourced record compiler powered by Blockchain that allows users to upload videos in various activities and see how you rank against other people. It allows you to unofficially join the prestigious Guinness World Record holders, and provides accessibility for anyone to “aSend” the ranks.

Through our website, users are allowed to upload their own videos to different categories and are ranked by some metric/value. For example, the categories can range from how many free throws you can make in a row to how fast you can speedrun the first level of Super Mario Bros. People’s uploads are then verified and then ranked alongside others’ submissions for the whole world to see.

aSend leverages the ElvClient API provided by eluv.io for content management. ElvClient allows users to post and stream high-quality videos on the content fabric which is a core functionality of aSend. But more importantly, the underlying contracts ingrained into the fabric provide authorized users a track of every access points and edits on their content with full integrity. This is the perfect interface for maintaining immutable ledgers of rankings and popularity of the video. We utilized the django framework to build the user interface which allows us to easily integrate the API calls and provided a data management portal to store metadata for each user.
