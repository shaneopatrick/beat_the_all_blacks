# ML Checklist

### Frame the Problem / Big Picture
> _1. Define the objective_

How to beat the All Blacks.

Mine historical rugby stats, as far back as possible, for All Black test matches looking at lossed/wins and attempt to uncover insights with the available data. Possible ML or SVD, PCA, or other methods.

> _2. How will your solution be used?_

Reading for anyone interested. Send formal deliverable to Jason Healy with NZRU.

> _3. What are the current solutions/workarounds (if any)?_

None that I'm aware of thus far.

> _4. How should you frame this problem (supervised/unsupervised,   online/offline, etc.)?_

* EDA to try and identify trends.

* Feature engineering as much as possible.

* Supervised learning. Have a serious class imbalance, may need to bootstrap the "W" examples and run training/testing multiple times.

* Alternatively could try to uncover most significant features using PCA, SVD, etc.

> _5. How should performance be measured?_

Have a hold out set of a few losses and some wins, test. Could also test on unseen stats from future matches to measure performance.

If feature importance only method available not sure how performance best measured...

> _6. Is the performance measure aligned with the objective?_

If can create predictive model measure accuracy, if not unsure...

> _7. What would be the minimum performance needed to meet the objective?_

Over 80% accuracy...

> _8. What are comparable problems? Can you reuse experience or tools?_

Not that I've found.

> _9. Is human expertise available?_

Nope.

> _10. How would you solve this problem manually?_

Not sure.

> _11. List the assumptions you (or others) have made so far._

* Assuming there are indeed some insights in the data
* The statistics provided are deep enough to gleam some insights
* The fact that wins and loses are measurable via rugby statistics


> _12. Verify assumptions if possible._

tbd...
