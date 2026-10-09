# Q&A drill (Fri night): what today's mentors actually asked, with short answers

Built from today's mentor talks.
Practise out loud: answer each in under 15 seconds, then stop talking.

## Corrections first: things said in the mentor talks that were wrong or vague
- ❌ "Several rivers flooding together is 4× more likely than one river flooding."
  ✅ **"Big flood springs, when 4 or more of our 14 rivers flood, happen almost 4× more often than if rivers
  flooded independently."** (15.4 % of springs observed vs 3.9 % by chance.)
- ❌ "We trained on 1961–2000 and the predictions for 2000–2025 came quite close."
  ✅ **"The snow still ranked the flood years on unseen recent years (correlation about 0.7), but snowy Marches
  became rare, so the exact ×3 is only confirmed on older years."**
- ❌ "I'm not sure what preparing means." ✅ See Q4.
- ❌ "I think we use QAE." ✅ **"We use quantum amplitude estimation, the maximum-likelihood version: the circuit
  with 0, 1 and 2 Grover steps, combined statistically."**

## The questions mentors and jurors will ask

**1. What is it, in one sentence?**
"An index that pays an insurer when several northern rivers flood in the same spring, priced from 65 years of
river data and updated every March from the snow."

**2. Who pays whom?**
"The insurer pays its reinsurer for flood cover that pays out automatically on our index, and pays us a licence:
€25k pilot, then €75k a year."

**3. Why would OP buy it? (lead with this one)**
"In March, two months before the melt, they know how risky this spring is, so they can buy extra cover from their
reinsurer in time, and prepare."

**4. What does "prepare" mean concretely?**
"Buy extra cover; line up claims adjusters and repair contractors in the risky regions; text customers to move
belongings up; set aside reserves and warn management early."

**5. How is your payout different from ordinary reinsurance?**
"Ordinary reinsurance pays actual losses after every claim is assessed: months. Ours pays on the river gauges:
days, nothing to argue about. The catch is basis risk, which the pilot measures."

**6. Why compare to the 0.27 / the regulator?**
"From 2027 the regulator's capital formula assumes an average link of 0.27 between Finnish flood zones. Insurers
anchor on it. Inside one region, rivers that share a snowpack are linked much more strongly, so the real cost is
about 1.8× higher."

**7. Why quantum at all?**
"Pricing rare floods means estimating tiny probabilities. Classical sampling needs four times the runs for twice
the accuracy; amplitude estimation needs only twice. On a perfect simulator it was 2.5× more accurate at the same
16,000 runs."

**8. So does quantum help today?**
"No. Classical still wins on today's noisy chips. The method is ready; the hardware isn't yet. We measured exactly
where it breaks on four real machines."

**9. What exactly is your circuit?**
"One qubit is the wet-spring state, one per river. Rotations set each river's flood chance from our model, and
controlled rotations link rivers to the wet spring, so they flood together. A CZ marks 'both flood', and Grover
steps amplify it."

**10. Did you try other feature maps / embeddings / scaling?**
"In amplitude estimation the encoding isn't a free choice like in quantum ML: each angle comes straight from a
probability, so the amplitude IS the probability. Rescaling would change the answer. We tuned calibration and
circuit depth instead."

**11. Why was Q50 worse than IBM and IQM?**
"On the qubits we got, Q50 misread a 0 as a 1 about 5 % of the time, vs under 2 % on IBM and IQM. With ten times
more shots the repeats agreed, but still read 2–3× high. Next we'd pick the best qubits and use error mitigation."

**12. Isn't the market tiny?**
"Finland alone is small: it's our proof market. Sweden, Norway and other snowmelt regions are next, and at scale
we'd take a small share of the premium on every cover using our index."

**13. Is it machine learning?**
"No, a statistical model: flood levels per river, a national and regional factor for how they move together, and
the snow's effect. With 65 springs, an explainable model beats ML."

**14. What's your ask?**
"One insurer's flood claims for eight weeks, to measure basis risk and give a firm quote."

## Strategy notes
- **Business beats tech with this jury.** Mentors said the business case is where the
  points are. Deliver slide 7 slowly and look at OP's juror.
- **Say "why quantum" once, clearly** (Q7), then be honest (Q8). Don't over-explain the circuit in the pitch;
  keep that for Q&A.
- **Q&A rule:** answer, give one number, stop. If unsure: "Good question; we haven't measured that yet. It's part
  of the pilot."
- **Split the answers:** whoever didn't present a slide takes the questions on it. Business questions are a good
  fit for Vaishnav once he has read Q2–Q6 and Q12.
