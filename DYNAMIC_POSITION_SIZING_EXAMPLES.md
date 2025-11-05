# Dynamic RL Confidence Position Sizing

## **How It Works:**
The bot **dynamically scales position size** based on:
1. **User's Max Contracts** (set in GUI: 1-25)
2. **RL Confidence Score** (0-100% from past trade data)

Formula: `contracts = max_contracts × confidence_multiplier`

---

## **Examples with Different Max Contract Settings:**

### **User Sets Max = 3 Contracts** (Conservative)
```
Confidence 20%: 3 × 0.36 = 1 contract   (minimum)
Confidence 40%: 3 × 0.52 = 2 contracts  (low confidence)
Confidence 60%: 3 × 0.68 = 2 contracts  (medium confidence)
Confidence 80%: 3 × 0.84 = 3 contracts  (high confidence)
Confidence 95%: 3 × 0.96 = 3 contracts  (very high confidence)
```

### **User Sets Max = 5 Contracts**
```
Confidence 20%: 5 × 0.36 = 2 contracts
Confidence 40%: 5 × 0.52 = 3 contracts
Confidence 60%: 5 × 0.68 = 3 contracts
Confidence 80%: 5 × 0.84 = 4 contracts
Confidence 95%: 5 × 0.96 = 5 contracts
```

### **User Sets Max = 10 Contracts** (Moderate)
```
Confidence 20%: 10 × 0.36 = 4 contracts
Confidence 40%: 10 × 0.52 = 5 contracts
Confidence 60%: 10 × 0.68 = 7 contracts
Confidence 80%: 10 × 0.84 = 8 contracts
Confidence 95%: 10 × 0.96 = 10 contracts
```

### **User Sets Max = 15 Contracts**
```
Confidence 20%: 15 × 0.36 = 5 contracts
Confidence 40%: 15 × 0.52 = 8 contracts
Confidence 60%: 15 × 0.68 = 10 contracts
Confidence 80%: 15 × 0.84 = 13 contracts
Confidence 95%: 15 × 0.96 = 14 contracts
```

### **User Sets Max = 25 Contracts** (Aggressive)
```
Confidence 20%: 25 × 0.36 = 9 contracts
Confidence 40%: 25 × 0.52 = 13 contracts
Confidence 60%: 25 × 0.68 = 17 contracts
Confidence 80%: 25 × 0.84 = 21 contracts
Confidence 95%: 25 × 0.96 = 24 contracts
```

---

## **Confidence Multiplier Formula:**

```python
def get_position_size_multiplier(confidence: float) -> float:
    """
    Linear scaling: 0% → 20%, 100% → 100%
    
    confidence = 0.0  → multiplier = 0.20 (minimum 20%)
    confidence = 0.5  → multiplier = 0.60 (60%)
    confidence = 1.0  → multiplier = 1.00 (100%)
    """
    multiplier = 0.2 + (confidence * 0.8)
    return max(0.2, min(1.0, multiplier))
```

---

## **Real Trading Examples:**

### **Scenario 1: Small Account, Conservative**
```
User Settings:
  Max Contracts: 3
  Account: $50,000
  Risk: 1.2% = $600

Trade Setup:
  RL Confidence: 35%
  Multiplier: 0.48
  Position Size: 3 × 0.48 = 1 contract ✅
  
Bot Log:
  [RL DYNAMIC SIZING] LOW confidence (35.0%) × Max 3 = 1 contracts (48.0%)
```

### **Scenario 2: Medium Account, Balanced**
```
User Settings:
  Max Contracts: 10
  Account: $100,000
  Risk: 1.2% = $1,200

Trade Setup:
  RL Confidence: 72%
  Multiplier: 0.78
  Position Size: 10 × 0.78 = 8 contracts ✅
  
Bot Log:
  [RL DYNAMIC SIZING] HIGH confidence (72.0%) × Max 10 = 8 contracts (78.0%)
```

### **Scenario 3: Large Account, Aggressive**
```
User Settings:
  Max Contracts: 25
  Account: $250,000
  Risk: 1.2% = $3,000

Trade Setup:
  RL Confidence: 88%
  Multiplier: 0.90
  Position Size: 25 × 0.90 = 23 contracts ✅
  
Bot Log:
  [RL DYNAMIC SIZING] VERY HIGH confidence (88.0%) × Max 25 = 23 contracts (90.0%)
```

### **Scenario 4: Low Confidence Trade**
```
User Settings:
  Max Contracts: 15
  Account: $150,000
  Risk: 1.2% = $1,800

Trade Setup:
  RL Confidence: 22%
  Multiplier: 0.38
  Position Size: 15 × 0.38 = 6 contracts ✅
  
Bot Log:
  [RL DYNAMIC SIZING] VERY LOW confidence (22.0%) × Max 15 = 6 contracts (38.0%)
```

---

## **Key Benefits:**

### **1. Always Scales to User's Limit**
- User sets max = 5 → Bot never exceeds 5 contracts
- User sets max = 25 → Bot can use up to 25 contracts
- **Fully dynamic to ANY number between 1-25**

### **2. Confidence-Based Risk Management**
- Low confidence (20-40%) → Small position (20-52% of max)
- Medium confidence (40-70%) → Moderate position (52-76% of max)
- High confidence (70-100%) → Large position (76-100% of max)

### **3. Never Goes to Zero**
- Minimum 1 contract even at 0% confidence
- Ensures bot can always learn from trades

### **4. Linear Scaling**
- Smooth, predictable sizing
- 50% confidence = 60% of max contracts
- No sudden jumps in position size

---

## **Customer Use Cases:**

### **Beginner Trader**
```
Max Contracts: 1-3
Why: Learning, small account, testing strategy
Result: Even at high confidence, max 3 contracts = controlled risk
```

### **Intermediate Trader**
```
Max Contracts: 5-10
Why: Growing account, proven strategy, scaling up
Result: Can leverage high confidence signals with 8-10 contracts
```

### **Advanced Trader**
```
Max Contracts: 15-25
Why: Large account, experienced, maximizing returns
Result: High confidence signals = 20+ contracts for big profits
```

### **Funded Trader (TopStep, etc.)**
```
Max Contracts: 5-10 (TopStep limit)
Why: Evaluation rules, profit targets
Result: Works within funded account contract limits
```

---

## **What Customers See in Logs:**

```
[RL DYNAMIC SIZING] MEDIUM confidence (55.0%) × Max 10 = 6 contracts (60.0%)
  Entry: $5000.00, Stop: $4994.00, Target: $5015.00
  Risk: 6.0 ticks ($300.00)
  Reward: 15.0 ticks (2.5:1 R/R)
  Position: 6 contracts
  Max Risk: $1,800 (1.2% of $150,000)
```

**Customer knows exactly:**
- Why 6 contracts? (55% confidence × max 10)
- Is this a good trade? (2.5:1 R/R ✅)
- How much can I lose? ($1,800 max)

---

## **Summary:**

✅ **Works with ANY max_contracts setting (1-25)**  
✅ **Dynamically scales based on RL confidence**  
✅ **Never exceeds user's limit**  
✅ **Transparent logging shows the math**  
✅ **Protects account with minimum position sizes**  

🎯 **The system is already 100% dynamic!** No matter what max_contracts the user chooses, the bot will intelligently scale position size based on how confident it is in the trade.
