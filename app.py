import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick  # Import ticker module

# Function to format numbers in Finnish style with one decimal
def format_number_finnish(value, is_percentage=False):
    # Check if the value is a number
    if isinstance(value, (int, float, np.integer, np.floating)):
        # Round to one decimal
        value = round(value, 1)
        if is_percentage:
            formatted = f"{value:,.1f} %".replace(',', ' ').replace('.', ',')
        else:
            # Separate thousands with space and decimals with comma
            formatted = f"{value:,.1f}".replace(',', ' ').replace('.', ',')
        return formatted
    else:
        return value

st.title('Asunto-ostajan laskuri')

# Sidebar inputs for Mortgage
st.sidebar.header('Asuntolainan parametrit')
loan_amount = st.sidebar.slider('Lainan kokonaissumma (€)', 0, 2_000_000, 300_000, step=10_000, format="%d")

# **Using "Vastike" for Maintenance Costs**
vastike = st.sidebar.slider('Vastike (€)', 0, 2_000, 100, step=100, format="%d")

# Asunnon arvo ostohetkellä
initial_property_value = st.sidebar.slider('Asunnon arvo ostohetkellä (€)', 0, 2_000_000, 300_000, step=10_000, format="%d")

loan_term = st.sidebar.slider('Laina-aika (vuodet)', 5, 40, 25, step=1)
loan_rate = st.sidebar.slider('Lainakorko (%)', 0.0, 10.0, 3.0, step=0.1, format="%.1f")

# Sidebar inputs for Investment
st.sidebar.header('Sijoittamisen parametrit')
starting_amount = st.sidebar.slider('Alkupääoma (€)', 0, 1_000_000, 0, step=10_000)
monthly_investment = st.sidebar.slider('Kuukausittainen sijoitus (€)', 0, 10_000, 500, step=100)
investment_rate = st.sidebar.slider('Sijoituksen tuottoprosentti (%)', 0, 20, 5, step=1)
active_investment_period = st.sidebar.slider('Aktiivinen sijoitusaika (vuodet)', 1, 40, 25, step=1)
age = st.sidebar.number_input('Nykyinen ikäsi', min_value=0, max_value=100, value=30, step=1)

# Sidebar inputs for Rent
st.sidebar.header('Vuokrauksen parametrit')
monthly_rent = st.sidebar.slider('Kuukausittainen vuokra (€)', 0, 4_000, 1_200, step=100)

# Sidebar inputs for Income
st.sidebar.header('Tulojen parametrit')
net_salary = st.sidebar.number_input('Nettokuukausipalkkasi (€)', min_value=0, value=3_000, step=100)

# Calculate passive investment period
pension_age = 69
passive_investment_period = pension_age - age - active_investment_period

if passive_investment_period < 0:
    st.error('Ikäsi ja aktiivisen sijoitusajan summa ylittää odotetun eliniän 69 vuotta. Ole hyvä ja tarkista syötteesi.')
    st.stop()

# Total investment period
total_investment_period = active_investment_period + passive_investment_period

# Investment years array
investment_years = np.arange(1, total_investment_period + 1)

# Mortgage calculations
years = np.arange(1, loan_term + 1)
months = loan_term * 12
monthly_interest_rate = loan_rate / 100 / 12

if monthly_interest_rate > 0:
    monthly_payment = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** months / ((1 + monthly_interest_rate) ** months - 1)
else:
    monthly_payment = loan_amount / months

# Initialize lists to store values
remaining_balance = loan_amount
monthly_payments = []
monthly_interests = []
monthly_principals = []
total_interest = 0
total_principal = 0

for i in range(1, months + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment

    # Store monthly values
    monthly_payments.append(monthly_payment)
    monthly_interests.append(interest_payment)
    monthly_principals.append(principal_payment)

    # Cumulative sums
    total_interest += interest_payment
    total_principal += principal_payment

# Convert monthly data to annual data
annual_payments = [sum(monthly_payments[i*12:(i+1)*12]) for i in range(loan_term)]
annual_interests = [sum(monthly_interests[i*12:(i+1)*12]) for i in range(loan_term)]
annual_principals = [sum(monthly_principals[i*12:(i+1)*12]) for i in range(loan_term)]
cumulative_annual_interest = np.cumsum(annual_interests)
cumulative_annual_principal = np.cumsum(annual_principals)
cumulative_mortgage_cost = cumulative_annual_interest + cumulative_annual_principal

# Calculate total amounts
total_interest_paid = cumulative_annual_interest[-1]
total_principal_paid = cumulative_annual_principal[-1]
total_mortgage_payments = total_interest_paid + total_principal_paid

# **Calculate total vastike (maintenance charges) during loan period**
total_vastike_paid = vastike * 12 * loan_term

# Investment calculations
annual_return_rate = investment_rate / 100

# Initialize investment values
cumulative_investment = []

for n in range(1, total_investment_period + 1):
    if n <= active_investment_period:
        # During active investment period
        if annual_return_rate != 0:
            future_value = starting_amount * (1 + annual_return_rate) ** n + \
                monthly_investment * 12 * ((1 + annual_return_rate) ** n - 1) / annual_return_rate
        else:
            future_value = starting_amount + monthly_investment * 12 * n
    else:
        # During passive investment period
        years_after_active = n - active_investment_period
        value_at_end_of_active = cumulative_investment[active_investment_period - 1]
        future_value = value_at_end_of_active * (1 + annual_return_rate) ** years_after_active
    cumulative_investment.append(future_value)

cumulative_investment = np.array(cumulative_investment)

# Adjust investment array to match the loan term years for the main plot
if total_investment_period < loan_term:
    adjusted_cumulative_investment = np.append(
        cumulative_investment,
        [cumulative_investment[-1]] * (loan_term - total_investment_period)
    )
elif total_investment_period > loan_term:
    adjusted_cumulative_investment = cumulative_investment[:loan_term]
else:
    adjusted_cumulative_investment = cumulative_investment

# Total investment amount at the end of the total investment period
total_investment = cumulative_investment[-1]

# Total investment over active and passive periods
if active_investment_period > 0:
    total_investment_active = cumulative_investment[active_investment_period - 1]
else:
    total_investment_active = 0

total_investment_passive = total_investment - total_investment_active

# Rent calculations
cumulative_rent = np.cumsum([monthly_rent * 12 for _ in years])

# Total rent paid
total_rent_paid = cumulative_rent[-1]

# **Prepare Summary Table with Separate Columns for Loan and Rent Scenarios**
# Calculate monthly expenses for mortgage scenario
annual_expenses_mortgage = total_mortgage_payments + total_vastike_paid
monthly_expenses_mortgage = annual_expenses_mortgage / (loan_term * 12)

# Calculate additional monthly investment for rent scenario
additional_monthly_investment = monthly_expenses_mortgage - monthly_rent if monthly_expenses_mortgage > monthly_rent else 0
additional_annual_investment = additional_monthly_investment * 12

if additional_monthly_investment > 0:
    # Calculate cumulative investments for rent scenario with additional investments
    cumulative_investment_rent = []
    for n in range(1, total_investment_period + 1):
        if n <= active_investment_period:
            # During active investment period
            if annual_return_rate != 0:
                future_value = starting_amount * (1 + annual_return_rate) ** n + \
                    (monthly_investment + additional_monthly_investment) * 12 * ((1 + annual_return_rate) ** n - 1) / annual_return_rate
            else:
                future_value = starting_amount + (monthly_investment + additional_monthly_investment) * 12 * n
        else:
            # During passive investment period
            years_after_active = n - active_investment_period
            value_at_end_of_active_new = cumulative_investment_rent[active_investment_period - 1]
            future_value_new = value_at_end_of_active_new * (1 + annual_return_rate) ** years_after_active
            future_value = value_at_end_of_active_new * (1 + annual_return_rate) ** years_after_active
        cumulative_investment_rent.append(future_value)

    cumulative_investment_rent = np.array(cumulative_investment_rent)

    # Adjust investment array to match the loan term years
    if total_investment_period < loan_term:
        adjusted_cumulative_investment_rent = np.append(
            cumulative_investment_rent,
            [cumulative_investment_rent[-1]] * (loan_term - total_investment_period)
        )
    elif total_investment_period > loan_term:
        adjusted_cumulative_investment_rent = cumulative_investment_rent[:loan_term]
    else:
        adjusted_cumulative_investment_rent = cumulative_investment_rent

    # Total investment amount at the end of the total investment period
    total_investment_rent = cumulative_investment_rent[-1]

    # Total investment over active and passive periods
    if active_investment_period > 0:
        total_investment_active_rent = cumulative_investment_rent[active_investment_period - 1]
    else:
        total_investment_active_rent = 0

    total_investment_passive_rent = total_investment_rent - total_investment_active_rent
else:
    # If no additional investment, rent scenario investments are same as loan scenario
    cumulative_investment_rent = cumulative_investment
    total_investment_rent = total_investment
    total_investment_active_rent = total_investment_active
    total_investment_passive_rent = total_investment_passive

summary_data = {
    'Erä': [
        'Kokonaiskorko maksettu laina-aikana',
        'Kokonaislyhennys maksettu laina-aikana',
        'Asuntolainan kokonaismaksut laina-aikana',
        'Kokonaisvastike maksettu laina-aikana',
        'Kokonaisvuokra maksettu laina-aikana',
        'Sijoitusten kokonaisarvo aktiivisena sijoitusaikana',
        'Sijoitusten kokonaisarvo passiivisena sijoitusaikana',
        'Sijoitusten kokonaisarvo sijoitusaikana',
        'Asunnon arvo kun laina-aika loppuu'
    ],
    'Asuntolaina skenaario (€)': [
        total_interest_paid,
        total_principal_paid,
        total_mortgage_payments,
        total_vastike_paid,
        np.nan,  # Not applicable for loan scenario
        total_investment_active,
        total_investment_passive,
        total_investment,
        initial_property_value * (1 + 0.02) ** loan_term  # Property value calculation
    ],
    'Vuokraus skenaario (€)': [
        np.nan,  # Not applicable for loan scenario
        np.nan,  # Not applicable for loan scenario
        np.nan,  # Not applicable for loan scenario
        np.nan,  # Not applicable for loan scenario
        total_rent_paid,
        total_investment_active_rent,
        total_investment_passive_rent,
        total_investment_rent,
        np.nan  # Not applicable for rent scenario
    ]
}

summary_df = pd.DataFrame(summary_data)

# Format numbers using the Finnish formatting function, handling NaN appropriately
for col in ['Asuntolaina skenaario (€)', 'Vuokraus skenaario (€)']:
    summary_df[col] = summary_df[col].apply(lambda x: format_number_finnish(x) if not pd.isna(x) else '-')

# Display Summary Totals Table without Index Columns
st.write('### Yhteenveto')
st.dataframe(summary_df)

# Plotting the main financial comparison
st.write('### Taloudellinen vertailu laina-ajan yli')

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(years, cumulative_mortgage_cost, label='Asuntolainan kokonaissumma', color='#1f77b4')
ax.plot(years, cumulative_annual_interest, label='Asuntolainan korko', color='#aec7e8', linestyle='--')
ax.plot(years, cumulative_annual_principal, label='Asuntolainan lyhennys', color='#ffbb78', linestyle='--')
ax.plot(years, adjusted_cumulative_investment, label='Sijoitukset', color='#2ca02c')
ax.plot(years, cumulative_rent, label='Vuokra', color='#ff7f0e')

ax.set_xlabel('Vuodet')
ax.set_ylabel('Kumulatiivinen summa (€)')
ax.set_title('Taloudellinen vertailu laina-ajan yli')
ax.legend()
ax.grid(True)

# Format y-axis with Finnish number formatting
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: format_number_finnish(x)))

st.pyplot(fig)

# Investment Growth Plot
st.write('### Sijoituksen kasvu eläkeikään asti')

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot(investment_years, cumulative_investment, label='Sijoituksen arvo ilman erotusta', color='#2ca02c')
if additional_monthly_investment > 0:
    ax2.plot(investment_years, cumulative_investment_rent, label='Sijoituksen arvo lisätyllä erolla', color='#d62728')

ax2.set_xlabel('Vuodet')
ax2.set_ylabel('Sijoituksen arvo (€)')
ax2.set_title('Sijoituksen vertailu')
ax2.legend()
ax2.grid(True)

# Format y-axis with Finnish number formatting
ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: format_number_finnish(x)))

st.pyplot(fig2)

# **Defining 'df' Variable for "Vuotuiset arvot (kumulatiivinen summa)"**
# Create DataFrame for Annual Values Table
data = {
    'Vuosi': years,
    'Asuntolainan kokonaissumma (€)': cumulative_mortgage_cost.astype(float),
    'Asuntolainan korko (€)': cumulative_annual_interest.astype(float),
    'Asuntolainan lyhennys (€)': cumulative_annual_principal.astype(float),
    'Sijoitukset (€)': adjusted_cumulative_investment.astype(float),
    'Vuokra (€)': cumulative_rent.astype(float)
}
df = pd.DataFrame(data)

# Format numbers using the Finnish formatting function
df['Asuntolainan kokonaissumma (€)'] = df['Asuntolainan kokonaissumma (€)'].apply(lambda x: format_number_finnish(x))
df['Asuntolainan korko (€)'] = df['Asuntolainan korko (€)'].apply(lambda x: format_number_finnish(x))
df['Asuntolainan lyhennys (€)'] = df['Asuntolainan lyhennys (€)'].apply(lambda x: format_number_finnish(x))
df['Sijoitukset (€)'] = df['Sijoitukset (€)'].apply(lambda x: format_number_finnish(x))
df['Vuokra (€)'] = df['Vuokra (€)'].apply(lambda x: format_number_finnish(x))

# Display Annual Values Table without Index Columns
st.write('### Vuotuiset arvot (kumulatiivinen summa)')
annual_values_df = df.reset_index(drop=True)
st.dataframe(annual_values_df)

# Net Salary Allocation Calculations

# Mortgage scenario calculations

# Get the first month's principal and interest payments
monthly_principal_payment = monthly_principals[0]
monthly_interest_payment = monthly_interests[0]
total_monthly_mortgage_payment = monthly_payment  # Total monthly mortgage payment

# Calculate percentages of net salary
if net_salary > 0:
    percentage_principal = (monthly_principal_payment / net_salary) * 100
    percentage_interest = (monthly_interest_payment / net_salary) * 100
    percentage_vastike = (vastike / net_salary) * 100  # Percentage for vastike
    percentage_total_mortgage = ((total_monthly_mortgage_payment + vastike) / net_salary) * 100
    percentage_investment_mortgage = (monthly_investment / net_salary) * 100
    total_expenses_mortgage = total_monthly_mortgage_payment + vastike + monthly_investment  # Added vastike
    percentage_left_mortgage = 100 - ((total_expenses_mortgage / net_salary) * 100)
    amount_left_mortgage = net_salary - total_expenses_mortgage
else:
    percentage_principal = percentage_interest = percentage_total_mortgage = percentage_vastike = percentage_investment_mortgage = percentage_left_mortgage = amount_left_mortgage = 0
    st.error("Nettopalkan on oltava suurempi kuin nolla prosenttilaskelmia varten.")

# Create a DataFrame for the mortgage scenario
mortgage_data = {
    'Erä': [
        'Kuukausittainen lyhennysmaksu',
        'Kuukausittainen korkomaksu',
        'Kuukausittainen vastike',  # Vastike
        'Asuntolainan kokonaiskuukausimaksu',
        'Kuukausittainen sijoitus',
        'Jäljelle jäävä summa kulujen jälkeen'
    ],
    'Nettopalkan prosenttiosuus (%)': [
        format_number_finnish(percentage_principal, is_percentage=True),
        format_number_finnish(percentage_interest, is_percentage=True),
        format_number_finnish(percentage_vastike, is_percentage=True),  # Percentage for vastike
        format_number_finnish(percentage_total_mortgage, is_percentage=True),
        format_number_finnish(percentage_investment_mortgage, is_percentage=True),
        format_number_finnish(percentage_left_mortgage, is_percentage=True)
    ],
    'Summa (€)': [
        format_number_finnish(monthly_principal_payment),
        format_number_finnish(monthly_interest_payment),
        format_number_finnish(vastike),  # Vastike
        format_number_finnish(total_monthly_mortgage_payment + vastike),  # Total mortgage + vastike
        format_number_finnish(monthly_investment),
        format_number_finnish(amount_left_mortgage)
    ]
}

mortgage_df = pd.DataFrame(mortgage_data)

# Display the mortgage scenario table without Index Columns
st.write('### Asuntolaina skenaario (€) - nettopalkan jakautuminen')
st.dataframe(mortgage_df)

# Renting scenario calculations

# Calculate percentages of net salary
if net_salary > 0:
    percentage_rent = (monthly_rent / net_salary) * 100
    percentage_investment_rent = (monthly_investment / net_salary) * 100
    total_expenses_rent = monthly_rent + monthly_investment
    percentage_left_rent = 100 - ((total_expenses_rent / net_salary) * 100)
    amount_left_rent = net_salary - total_expenses_rent
else:
    percentage_rent = percentage_investment_rent = percentage_left_rent = amount_left_rent = 0
    st.error("Nettopalkan on oltava suurempi kuin nolla prosenttilaskelmia varten.")

# Create a DataFrame for the renting scenario
rent_data = {
    'Erä': [
        'Kuukausittainen vuokramaksu',
        'Kuukausittainen sijoitus',
        'Jäljelle jäävä summa kulujen jälkeen'
    ],
    'Nettopalkan prosenttiosuus (%)': [
        format_number_finnish(percentage_rent, is_percentage=True),
        format_number_finnish(percentage_investment_rent, is_percentage=True),
        format_number_finnish(percentage_left_rent, is_percentage=True)
    ],
    'Summa (€)': [
        format_number_finnish(monthly_rent),
        format_number_finnish(monthly_investment),
        format_number_finnish(amount_left_rent)
    ]
}

# **Include additional investments in the rent scenario if applicable**
if additional_monthly_investment > 0:
    rent_data['Erä'].extend([
        'Kuukausittainen lisäsijoitus',
        'Sijoitusten kokonaisarvo vuokrausskenaariossa'
    ])
    rent_data['Nettopalkan prosenttiosuus (%)'].extend([
        format_number_finnish((additional_monthly_investment / net_salary) * 100, is_percentage=True),
        format_number_finnish((total_investment_rent / net_salary) * 100, is_percentage=True)
    ])
    rent_data['Summa (€)'].extend([
        format_number_finnish(additional_monthly_investment),
        format_number_finnish(total_investment_rent)
    ])

rent_df = pd.DataFrame(rent_data)

# Display the renting scenario table without Index Columns
st.write('### Vuokraus skenaario (€) - nettopalkan jakautuminen')
st.dataframe(rent_df)

# Calculate the difference between "Jäljelle jäävä summa kulujen jälkeen" after renting and taking the loan
difference = amount_left_rent - amount_left_mortgage
st.write('### Ero nettosummissa kulujen jälkeen')
if difference > 0:
    st.write(f"Ero asuntolaina- ja vuokraus-skenaarioiden välillä on: **€{format_number_finnish(difference)}**")
    
    # Add the difference to the existing monthly investment
    new_monthly_investment = monthly_investment + difference
    st.write(f"Lisätään tämä ero kuukausittaiseen sijoitukseen: **€{format_number_finnish(difference)}**")
    
    # New investment calculations with increased monthly investment
    cumulative_investment_new = []
    for n in range(1, total_investment_period + 1):
        if n <= active_investment_period:
            # During active investment period
            if annual_return_rate != 0:
                future_value_new = starting_amount * (1 + annual_return_rate) ** n + \
                    new_monthly_investment * 12 * ((1 + annual_return_rate) ** n - 1) / annual_return_rate
            else:
                future_value_new = starting_amount + new_monthly_investment * 12 * n
        else:
            # During passive investment period
            years_after_active = n - active_investment_period
            value_at_end_of_active_new = cumulative_investment_new[active_investment_period - 1]
            future_value_new = value_at_end_of_active_new * (1 + annual_return_rate) ** years_after_active
        cumulative_investment_new.append(future_value_new)

    cumulative_investment_new = np.array(cumulative_investment_new)

    # Adjust investment array to match the loan term years
    if total_investment_period < loan_term:
        adjusted_cumulative_investment_new = np.append(
            cumulative_investment_new,
            [cumulative_investment_new[-1]] * (loan_term - total_investment_period)
        )
    elif total_investment_period > loan_term:
        adjusted_cumulative_investment_new = cumulative_investment_new[:loan_term]
    else:
        adjusted_cumulative_investment_new = cumulative_investment_new

    # Total investment amount at the end of the total investment period
    total_investment_new = cumulative_investment_new[-1]

    # Total investment over active and passive periods
    if active_investment_period > 0:
        total_investment_active_new = cumulative_investment_new[active_investment_period - 1]
    else:
        total_investment_active_new = 0

    total_investment_passive_new = total_investment_new - total_investment_active_new

    # Plot the investment scenarios
    st.write('### Sijoituksen vertailu')

    fig_new, ax_new = plt.subplots(figsize=(10, 6))
    ax_new.plot(investment_years, cumulative_investment, label='Sijoituksen arvo ilman erotusta', color='#2ca02c')
    ax_new.plot(investment_years, cumulative_investment_new, label='Sijoituksen arvo lisätyllä erolla', color='#d62728')
    
    ax_new.set_xlabel('Vuodet')
    ax_new.set_ylabel('Sijoituksen arvo (€)')
    ax_new.set_title('Sijoituksen vertailu')
    ax_new.legend()
    ax_new.grid(True)
    
    # Format y-axis with Finnish number formatting
    ax_new.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: format_number_finnish(x)))
    
    st.pyplot(fig_new)
    
    # Compute net worth for comparison
    property_value_end = initial_property_value * (1 + 0.02) ** loan_term  # Updated property value calculation
    net_worth_house = total_investment + property_value_end
    net_worth_rent = total_investment_new
    difference_net_worth = net_worth_house - net_worth_rent

else:
    st.write("Asuntolaina- ja vuokrausskenaarioiden välillä ei ole ylimääräistä rahaa sijoitettavaksi.")
    property_value_end = initial_property_value * (1 + 0.02) ** loan_term  # Updated property value calculation
    net_worth_house = total_investment + property_value_end
    net_worth_rent = total_investment  # No extra investment
    difference_net_worth = net_worth_house - net_worth_rent

# Function to generate financial advice
def generate_financial_advice(
    total_mortgage_payments,
    total_rent_paid,
    total_investment,
    amount_left_mortgage,
    amount_left_rent,
    net_salary,
    total_expenses_mortgage,
    total_expenses_rent,
    total_investment_active,
    total_investment_passive,
    passive_investment_period,
    active_investment_period,
    difference,
    total_investment_new,
    total_investment_active_new,
    total_investment_passive_new,
    property_value_end,
    net_worth_house,
    net_worth_rent,
    difference_net_worth,
    total_vastike_paid  # New parameter for vastike
):
    # Analyze the financial data and generate advice
    advice = ""
    
    # Compare renting and buying
    if (total_mortgage_payments + total_vastike_paid) < total_rent_paid:
        advice += "Asuntolainan kokonaismaksut ja vastikkeet ovat pienemmät kuin maksettu vuokra laina-aikana. Oman asunnon ostaminen voi olla taloudellisesti kannattavampaa pitkällä aikavälillä.\n\n"
    else:
        advice += "Maksettu vuokra laina-aikana on pienempi kuin asuntolainan kokonaismaksut ja vastikkeet. Vuokraaminen saattaa olla edullisempaa tämän ajanjakson aikana.\n\n"
    
    # Compare total rent paid with total interest paid during loan period
    rent_vs_interest_difference = abs(total_rent_paid - (total_mortgage_payments + total_vastike_paid))
    advice += f"Kokonaisvuokra maksettu laina-aikana on {format_number_finnish(total_rent_paid)} €, kun taas kokonaiskorko ja vastike maksettu laina-aikana on {format_number_finnish(total_mortgage_payments + total_vastike_paid)} €. "
    if rent_vs_interest_difference <= (total_mortgage_payments + total_vastike_paid) * 0.1:  # Within 10%
        advice += "Koska vuokra- ja korko-vastike-maksujen erotus on pieni, asuntolainan ottaminen ja asunnon ostaminen voi olla järkevää.\n\n"
    else:
        advice += "Koska vuokra- ja korko-vastike-maksujen erotus on merkittävä, kannattaa harkita tarkkaan asuntolainan ottamista.\n\n"
    
    # Comment on monthly budget distribution
    mortgage_budget_percentage = ((total_expenses_mortgage) / net_salary) * 100
    rent_budget_percentage = ((total_expenses_rent) / net_salary) * 100
    
    advice += f"Asuntolainaskenaariossa kuukausittaiset kulut ovat {format_number_finnish(total_expenses_mortgage)} € (laina- ja sijoituskulut), mikä on {format_number_finnish(mortgage_budget_percentage, is_percentage=True)} nettokuukausituloistasi.\n"
    advice += f"Vuokrausskenaariossa kuukausittaiset kulut ovat {format_number_finnish(total_expenses_rent)} € (vuokra- + sijoituskulut), mikä on {format_number_finnish(rent_budget_percentage, is_percentage=True)} nettokuukausituloistasi.\n\n"
    
    # Discuss net wealth during loan period and lifetime
    advice += f"Aktiivisen sijoitusajan ({active_investment_period} vuotta) aikana sijoitustesi arvo kasvaa {format_number_finnish(total_investment_active)} €.\n"
    advice += f"Passiivisen sijoitusajan ({passive_investment_period} vuotta) aikana sijoitustesi arvo kasvaa {format_number_finnish(total_investment_passive)} €.\n"
    advice += f"Sijoitusten kokonaisarvo sijoitusajan lopussa on {format_number_finnish(total_investment)} €.\n\n"
    
    # Add information about the difference and new investment scenario
    if difference > 0:
        advice += f"Vuokraskenaariossa {format_number_finnish(difference)} € enemmän on sijoitettu kuukausittaain. Tämä ylimääräinen kuukausittainen sijoitus kasvattaa sijoitustesi kokonaisarvoa siihen asti, kunnes pääset eläkkeelle.\n"
        # Calculate percentage increase in net worth due to the difference
        if total_investment > 0:
            percentage_increase = ((total_investment_new - total_investment) / total_investment) * 100
            advice += f"Sijoitustesi kokonaisarvo lisätyllä erolla on {format_number_finnish(total_investment_new)} €, mikä on {format_number_finnish(percentage_increase)} % enemmän kuin ilman erotusta.\n\n"
        else:
            advice += f"Sijoitustesi kokonaisarvo lisätyllä erolla on {format_number_finnish(total_investment_new)} €.\n\n"
    
    # Add information about property value with bold text
    advice += f"**Asunnon arvo kun laina-aika loppuu:** {format_number_finnish(property_value_end)} €.\n\n"
    
    # Compare net worth in both scenarios
    advice += "### Nettovarallisuuden vertailu\n\n"
    if net_worth_house > net_worth_rent:
        difference_net_worth_formatted = format_number_finnish(abs(difference_net_worth))
        advice += f"Asuntolaina- ja sijoitusskenaariossa nettovarallisuutesi eläkkeelle jäätyäsi on suurempi kuin vuokraus- ja sijoitusskenaariossa. Ero on **€{difference_net_worth_formatted}**.\n\n"
    elif net_worth_house < net_worth_rent:
        difference_net_worth_formatted = format_number_finnish(abs(difference_net_worth))
        advice += f"Vuokraus- ja sijoitusskenaariossa nettovarallisuutesi eläkkeelle jäätyäsi on suurempi kuin asuntolaina- ja sijoitusskenaariossa. Ero on **€{difference_net_worth_formatted}**.\n\n"
    else:
        advice += "Asuntolaina- ja vuokrausskenaarioissa nettovarallisuutesi eläkkeelle jäätyäsi on sama.\n\n"
    
    advice += "\n"
    # Consolidated disclaimers at the end
    
    # Suggest using extra money for investments based on scenarios
    advice += "\n### Suositukset osto- ja vuokrausskenaareihin perustuen\n\n"
    
    # Scenario 1: Low Percentage of Income Spent on Mortgage
    if mortgage_budget_percentage < 30:
        advice += "#### Hyvä tilanne ottaa asuntolaina\n"
        advice += "- **Nettotulo:** Vähän yli 3 000 € kuukaudessa.\n"
        advice += "- **Asuntolainan osuus nettotulosta:** Alle 30 %, mikä tarkoittaa, että sinulla on riittävästi tuloja kattamaan lainan, vastikkeet ja muiden kulujen lisäksi myös sijoituksia.\n"
        advice += "- **Oma omistus laina-aikana ja laina-aika päätyttyä:** Asunto on omistuksessasi, etkä joudu maksamaan lainan korkoja enää.\n\n"
    
    # Scenario 2: Moderate Percentage of Income Spent on Mortgage
    if 30 <= mortgage_budget_percentage < 40:
        advice += "#### Kohtalainen tilanne ottaa asuntolaina\n"
        advice += "- **Nettotulo:** Keskitasoinen, riittää lainan kattamiseen, mutta sijoituksiin jää vähemmän rahaa.\n"
        advice += "- **Asuntolainan osuus nettotulosta:** 30-40 %, mikä on sallittua, mutta varo liiallista sitoutumista talouteen.\n\n"
    
    # Scenario 3: High Rent vs. Interest Comparison
    if rent_vs_interest_difference <= (total_mortgage_payments + total_vastike_paid) * 0.1:
        advice += "#### Vuokra ja korko ovat samansuuruiset\n"
        advice += "- Vuokra- ja korko-vastike-maksujen lähellä oleva ero tekee asuntolainan ottamisesta ja asunnon ostamisesta houkuttelevan vaihtoehdon, sillä omistusasunto luo pitkäaikaista varallisuutta.\n\n"
    
    # Scenario 4: Continuous Rent vs. Ownership Post-Loan
    if loan_term > 20:  # Assuming long-term ownership
        advice += "#### Pitkäaikainen omistusasunto\n"
        advice += "- Laina-aikana maksamasi korkojen ja vastikkeiden jälkeen sinulla on oma asunto ilman kuukausittaisia lainakuluja, mikä voi merkittävästi vähentää kuukausittaisia kuluja eläkkeelle jäätyttyäsi.\n\n"
    
    # Scenario 5: Investment Growth Potential
    if difference > 0 and (total_investment_new > total_investment):
        advice += "#### Investointimahdollisuudet\n"
        advice += "- Lisätty sijoitus ero aiheuttaa merkittävän kasvun sijoitustesi arvossa, mikä parantaa nettovarallisuuttasi merkittävästi eläkkeelle päästyäsi.\n\n"
    
    # Scenario 6: Rent Continuity
    if net_worth_house > net_worth_rent:
        advice += "#### Vuokra jatkuvasti elämän aikana\n"
        advice += "- Jos jatkat vuokraamista elämän aikana, kuukausittaiset vuokrakulut jatkuvat, kun taas omistusasunnossa maksat vain kiinteitä lainakuluja ja vastikkeita laina-aikan jälkeen.\n\n"
    
    # Scenario 7: Financial Stability and Ownership Security
    advice += "#### Taloudellinen vakaus ja omistuksen turva\n"
    advice += "- Omistusasunto tarjoaa taloudellisen vakauden, sillä se ei ole riippuvainen vuokranantajan päätöksistä, kuten vuokrankorotuksista tai asunnon myymisestä.\n\n"
    
    return advice

# Call the advice function with the new parameter for vastike
advice_text = generate_financial_advice(
    total_mortgage_payments,
    total_rent_paid,
    total_investment,
    amount_left_mortgage,
    amount_left_rent,
    net_salary,
    total_expenses_mortgage,
    total_expenses_rent,
    total_investment_active,
    total_investment_passive,
    passive_investment_period,
    active_investment_period,
    difference,
    total_investment_new if additional_monthly_investment > 0 else 0,
    total_investment_active_new if additional_monthly_investment > 0 else 0,
    total_investment_passive_new if additional_monthly_investment > 0 else 0,
    property_value_end,
    net_worth_house,
    net_worth_rent,
    difference_net_worth,
    total_vastike_paid  # Passing the vastike
)

# Display the financial advice
st.write('### Henkilökohtainen taloudellinen analyysi')
st.write(advice_text)

# New cell with personal and bank interest calculations

import numpy as np

# Debt-to-Income (DTI) Ratio
# Use monthly mortgage payment, maintenance (vastike) as debt payments
total_monthly_debt_payments = monthly_payment + vastike
gross_monthly_income = net_salary  # Replace with gross income if available
dti_ratio = (total_monthly_debt_payments / gross_monthly_income) * 100 if gross_monthly_income > 0 else np.nan

# Loan-to-Value (LTV) Ratio
ltv_ratio = (loan_amount / initial_property_value) * 100 if initial_property_value > 0 else np.nan

# Monthly Payment Estimate (PITI) - simplified to mortgage + maintenance (vastike)
total_monthly_piti = monthly_payment + vastike
piti_percentage_income = (total_monthly_piti / gross_monthly_income) * 100 if gross_monthly_income > 0 else np.nan

# Affordability Index (AI) - should be >1 to be considered affordable
monthly_expenses = vastike + monthly_investment
affordability_index = (gross_monthly_income - total_monthly_debt_payments - monthly_expenses) / total_monthly_piti if total_monthly_piti > 0 else np.nan

# Expected Appreciation and Equity Growth
annual_appreciation_rate = 0.02  # Assuming 2% annual appreciation
future_property_value = initial_property_value * (1 + annual_appreciation_rate) ** loan_term

# Creating a DataFrame to summarize the calculations
calculations_data = {
    "Mittari": [
        "Velan suhde tuloihin (DTI)",
        "Laina-suhde arvoon (LTV)",
        "Kuukausittainen PITI",
        "PITI nettokuukausitulojen prosenttiosuutena",
        "Asumisen varaa mittari (AI)",
        "Odotettu arvonnousu laina-ajan lopussa"
    ],
    "Arvo": [
        f"{format_number_finnish(dti_ratio, is_percentage=True)}" if not np.isnan(dti_ratio) else "-",
        f"{format_number_finnish(ltv_ratio, is_percentage=True)}" if not np.isnan(ltv_ratio) else "-",
        f"{format_number_finnish(total_monthly_piti)} €",
        f"{format_number_finnish(piti_percentage_income, is_percentage=True)}" if not np.isnan(piti_percentage_income) else "-",
        format_number_finnish(affordability_index) if not np.isnan(affordability_index) else "-",
        f"{format_number_finnish(future_property_value)} €"
    ]
}

# Creating a DataFrame to display
financial_analysis_df = pd.DataFrame(calculations_data)

# Display the analysis table
st.write("### Taloudelliset mittarit lainapäätöksen tueksi")
st.dataframe(financial_analysis_df)

# Abbreviations and definitions in Finnish and English
st.write("""
---
### Lyhenteet ja niiden laskentatavat
**Velan suhde tuloihin (DTI) - Debt-to-Income Ratio:** Velan (kuukausittaisen asuntolainan maksuerän, vastikkeen ja sijoituksen) suhde kuukausituloihin. Laskenta: `DTI = (velan kuukausimaksut / kuukausitulot) * 100`.

**Laina-suhde arvoon (LTV) - Loan-to-Value Ratio:** Lainan suhde asunnon arvoon ostohetkellä. Laskenta: `LTV = (lainasumma / asunnon arvo) * 100`.

**Kuukausittainen PITI - Monthly Payment Estimate (PITI):** Yhdistetty kuukausittainen maksuerä, joka sisältää asuntolainan lyhennykset ja vastikkeen. Laskenta: `PITI = kuukausittainen asuntolaina + vastike`.

**PITI nettokuukausitulojen prosenttiosuutena - PITI as Percentage of Monthly Income:** PITI:n prosentuaalinen osuus kuukausittaisesta nettotulosta. Laskenta: `PITI osuus = (PITI / kuukausitulot) * 100`.

**Asumisen varaa mittari (AI) - Affordability Index (AI):** Arvioi, onko asuntolainan maksaminen taloudellisesti kestävää. Arvon tulisi olla yli 1, jotta asuminen katsotaan edulliseksi. Laskenta: `AI = (kuukausitulot - velan kuukausimaksut - muut kuukausikulut) / PITI`.

**Odotettu arvonnousu laina-ajan lopussa - Expected Appreciation and Equity Growth:** Ennustettu asunnon arvo laina-ajan lopussa, oletuksena 2% vuotuinen arvonnousu. Laskenta: `Arvonnousu = asunnon arvo * (1 + vuotuinen arvonnousu) ** laina-aika`.
""")


# Consolidated disclaimers at the end
st.write("""
---
**Disclaimer:**
- Odotettu eläkeikä on 69 vuotta.
- Oletettu 2% vuotuinen arvonnousu asunnolle.
""")

# Fine print section with reduced font size while maintaining LaTeX rendering
# Start with reduced font size using HTML
st.markdown("""
<div style="font-size: 0.7em;">
""", unsafe_allow_html=True)

# Display formulas and explanations
# Collapsible section for "Laskukaavat" with reduced font size
with st.expander("Laskukaavat"):
    st.markdown("""
    <div style="font-size: 0.7em;">
    """, unsafe_allow_html=True)

    st.write("#### Asuntolainan laskukaavat")
    st.latex(r"""
    M = P \cdot \frac{r(1+r)^n}{(1+r)^n - 1}
    """)
    st.markdown(r"""
    missä:
    - $M$: kuukausittainen maksuerä
    - $P$: lainan kokonaissumma
    - $r$: kuukausittainen korko (vuosikorko jaettuna 12:lla)
    - $n$: kokonaiserien lukumäärä (vuodet × 12)
    """)

    st.write("#### Sijoitusten laskukaavat")
    # Future value during active investment period
    st.latex(r"""
    FV = PV \cdot (1 + r)^n + PMT \cdot \frac{(1 + r)^n - 1}{r}
    """)
    st.markdown(r"""
    missä:
    - $FV$: sijoituksen tuleva arvo
    - $PV$: alkupääoma
    - $r$: vuotuinen tuottoprosentti (desimaalimuodossa)
    - $n$: sijoitusvuodet
    - $PMT$: kuukausittainen sijoitus
    """)

    # Future value during passive investment period
    st.latex(r"""
    FV_{\text{passive}} = FV_{\text{active}} \cdot (1 + r)^{n_{\text{passive}}}
    """)
    st.markdown(r"""
    missä:
    - $FV_{\text{active}}$: sijoituksen arvo aktiivisen sijoitusajan lopussa
    - $n_{\text{passive}}$: passiivisen ajan vuosimäärä
    """)

    st.write("#### Vuokran kumulatiivinen summa")
    # Cumulative rent formula
    st.latex(r"""
    \text{Kumulatiivinen vuokra} = \text{Kuukausivuokra} \times 12 \times n
    """)
    st.markdown(r"""
    missä:
    - **Kuukausivuokra**: Vuokran määrä kuukaudessa
    - $n$: Vuokrauksen vuosimäärä
    """)

    st.write("#### Nettopalkan jakautuminen")
    # Net salary percentage formula
    st.latex(r"""
    \text{Prosenttiosuus} = \left( \frac{\text{Kulut}}{\text{Nettopalkka}} \right) \times 100
    """)
    st.markdown(r"""
    missä:
    - **Kulut**: Kuukausittainen kuluerä (esim. asuntolainan maksuerä, vuokra, sijoitus, vastike)
    - **Nettopalkka**: Kuukausittainen nettopalkka
    """)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
