import streamlit as st
import pandas as pd

# --- Ustawienia Strony i Stan Sesji ---
st.set_page_config(layout="wide", title="Prosty Magazyn Towarów")

# Inicjalizacja stanu magazynu
# Używamy st.session_state do przechowywania danych, aby były trwałe
# podczas interakcji użytkownika.
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['Nazwa Towaru', 'Ilość', 'Cena (PLN)'])

# --- Funkcje Zarządzania Magazynem ---

def add_item(name, quantity, price):
    """Dodaje nowy towar do magazynu."""
    # Tworzenie nowego wiersza danych
    new_data = {'Nazwa Towaru': [name], 'Ilość': [quantity], 'Cena (PLN)': [price]}
    new_df = pd.DataFrame(new_data)
    
    # Łączenie z istniejącymi danymi w st.session_state
    st.session_state.inventory = pd.concat(
        [st.session_state.inventory, new_df], 
        ignore_index=True
    )
    st.success(f"Dodano: {name} (Ilość: {quantity})")

def remove_item(index_to_remove):
    """Usuwa towar na podstawie jego indeksu (numeru wiersza w tabeli)."""
    try:
        # Usuwamy wiersz z DataFrame na podstawie globalnego indeksu
        st.session_state.inventory = st.session_state.inventory.drop(
            st.session_state.inventory.index[index_to_remove]
        ).reset_index(drop=True)
        st.warning(f"Usunięto towar o indeksie: {index_to_remove}")
    except IndexError:
        st.error("Błąd: Nieprawidłowy numer indeksu do usunięcia.")


# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów v1.0")
st.markdown("Aplikacja do zarządzania zapasami w magazynie (Dodawanie, Usuwanie, Wyświetlanie).")

st.markdown("---")

# 1. Panel Dodawania Towaru
with st.expander("➕ DODAJ NOWY TOWAR", expanded=True):
    st.header("Wprowadź dane nowego towaru")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_name = st.text_input("Nazwa Towaru", key="new_name")
    with col2:
        # st.number_input zapewnia, że wprowadzane są tylko liczby całkowite i są >= 0
        new_quantity = st.number_input("Ilość", min_value=1, value=1, step=1, key="new_quantity")
    with col3:
        # Cena może być zmiennoprzecinkowa
        new_price = st.number_input("Cena jednostkowa (PLN)", min_value=0.01, value=10.00, step=0.50, key="new_price")
    
    if st.button("Dodaj do Magazynu", key="add_btn"):
        if new_name:
            add_item(new_name, new_quantity, new_price)
        else:
            st.error("Proszę podać nazwę towaru.")

st.markdown("---")

# 2. Wyświetlanie Magazynu
st.header("📊 Aktualny Stan Magazynu")

if st.session_state.inventory.empty:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar powyżej!")
else:
    # Wyświetlenie tabeli z danymi
    # Dodajemy kolumnę Index dla ułatwienia usuwania
    display_df = st.session_state.inventory.copy()
    display_df.index = display_df.index.rename('Index')
    display_df['Index'] = display_df.index
    
    # Zmieniamy kolejność kolumn
    display_df = display_df[['Index', 'Nazwa Towaru', 'Ilość', 'Cena (PLN)']]
    
    # Stosujemy formatowanie dla kolumny Ceny
    st.dataframe(
        display_df.style.format({'Cena (PLN)': "pln {:.2f}"}), 
        hide_index=True,
        use_container_width=True
    )

    # Obliczenia podsumowujące
    total_items = st.session_state.inventory['Ilość'].sum()
    total_value = (st.session_state.inventory['Ilość'] * st.session_state.inventory['Cena (PLN)']).sum()
    
    col_sum1, col_sum2 = st.columns(2)
    col_sum1.metric("Łączna Liczba Towarów", f"{total_items} szt.")
    col_sum2.metric("Łączna Wartość Magazynu", f"{total_value:.2f} PLN")

st.markdown("---")

# 3. Panel Usuwania Towaru
if not st.session_state.inventory.empty:
    with st.expander("➖ USUŃ TOWAR", expanded=False):
        st.subheader("Usuń towar po numerze Index")
        
        # Wybór numeru indeksu (wiersza) do usunięcia
        max_index = len(st.session_state.inventory) - 1
        
        index_to_remove = st.number_input(
            "Wprowadź Index towaru do usunięcia (patrz tabela powyżej)", 
            min_value=0, 
            max_value=max_index, 
            step=1, 
            key="remove_index"
        )
        
        # Kontrola, czy wybrany indeks jest poprawny
        if index_to_remove <= max_index:
             st.info(f"Wybrano do usunięcia: **{st.session_state.inventory.loc[index_to_remove, 'Nazwa Towaru']}**")

        if st.button("Usuń Towar", key="remove_btn"):
            remove_item(index_to_remove)
            st.rerun() # Odświeżenie aplikacji po usunięciu
