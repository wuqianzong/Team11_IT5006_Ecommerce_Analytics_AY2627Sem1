Dear Students,
As you work on Phase 2, remember that your marks depend on the quality of your foundational work, not the sophistication of your model. Here is what to focus on.

1. Problem Scoping (get this right first)

Define 1 or 2 problems maximum, covering both classification and regression
Identify a clear business stakeholder (operations, customer experience, seller management)
Confirm your target variable is either present or is derivable from the Olist tables
Confirm all predictors are known before the outcome occurs (no leakage)
2. Data Preparation

If your problem is customer-level, group/join on customer_unique_id, not customer_id
Do not use post-outcome columns as predictors.
Use scikit-learn Pipelines so preprocessing fits inside CV folds, not before them
If your target is imbalanced, have a plan (stratified splits, appropriate metrics, etc.)
3. Feature Engineering

Every engineered feature needs a rationale, not just a technical description
Where possible, ground your feature choices in findings from your Phase 1 literature review. If a paper you reviewed used specific feature transformations or domain-informed variables for e-commerce or transactional data, cite it and explain why it applies to your problem
This is where your literature review should pay off. Connect what you read to what you build
4. Modelling (Quality Over Quantity)

Start with the simplest variant in each family (e.g. plain LogisticRegression before regularised versions, single DecisionTree before RandomForest)
Every more complex model must demonstrate improvement over its family's baseline
A well-evaluated comparison of 2-3 models with clear business interpretation is worth more than a long list of poorly tuned models
5. Evaluation

Justify your choice of evaluation metrics. If your literature review covered how similar problems were evaluated, reference that work and cite it.
Use cross-validation with documented random seeds
Do not rely on accuracy alone for imbalanced targets
Analyse feature importance and connect findings back to business context
6. Common pitfalls to avoid

Jumping to an advanced model with no baseline
Random splits on temporal data (use stratified splits for imbalanced classes)
Features included without rationale
Reporting only aggregate metrics with no error analysis
Missing comparison of Train-Validate-Test results
Skipping the limitations discussion
I sincerely hope this helps you do better but if you are not sure about something, it is your duty as a team to ask.

Refer to the full project description for details: https://prakashsukhwal.github.io/IT5006/IT5006_Project_Description_2026Aug_V2.html
