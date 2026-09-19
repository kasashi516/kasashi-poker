import streamlit as st
from treys import Card, Deck, Evaluator
from itertools import combinations

st.set_page_config(page_title="德州撲克即時勝率計算機", layout="wide")

# 初始化 Session State
if 'hero_cards' not in st.session_state: st.session_state.hero_cards = ['Ah', 'Kh']
if 'hero2_cards' not in st.session_state: st.session_state.hero2_cards = []  # 第二副手牌
if 'hero3_cards' not in st.session_state: st.session_state.hero3_cards = []  # 第三副手牌
if 'villain_cards' not in st.session_state: st.session_state.villain_cards = []
if 'board_cards' not in st.session_state: st.session_state.board_cards = []
if 'active_target' not in st.session_state: st.session_state.active_target = 'hero'
if 'game_mode' not in st.session_state: st.session_state.game_mode = '單牌手模式'  # 預設單牌手

# 歷史紀錄變數：用來儲存上一把牌的狀態
if 'prev_hero_cards' not in st.session_state: st.session_state.prev_hero_cards = []
if 'prev_hero2_cards' not in st.session_state: st.session_state.prev_hero2_cards = []
if 'prev_hero3_cards' not in st.session_state: st.session_state.prev_hero3_cards = []
if 'prev_villain_cards' not in st.session_state: st.session_state.prev_villain_cards = []
if 'prev_board_cards' not in st.session_state: st.session_state.prev_board_cards = []

st.title("♠♥♦♣ 德州撲克即時歐印勝率計算機 ♣♦♥♠")

# 強制覆寫 primary 按鈕顏色，並特別針對右側選牌按鈕放大至 25px、高度 60px
st.markdown("""
    <style>
    /* 一般按鈕預設樣式 */
    div.stButton > button {
        width: 100%;
        height: 40px;
        font-size: 14px;
        font-weight: bold;
        border-radius: 6px;
        padding: 0px;
    }
    
    /* 專門針對右側欄（點擊選牌區）的按鈕放大字體至 25px 並調整高度 */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) div.stButton > button {
        font-size: 25px !important;
        height: 60px !important;
    }
    
    /* 縮小 Streamlit 區塊與標題的上下距離 */
    div.block-container {
        padding-top: 1.5rem;
    }
    h3 {
        padding-top: 0px !important;
        padding-bottom: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    hr {
        margin-top: 0.8rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* 強制將所有被選中（primary）的按鈕改為天藍色 */
    button[kind="primary"], [data-testid="baseButton-primary"] {
        background-color: #38bdf8 !important;
        border-color: #0ea5e9 !important;
        color: #0f172a !important;
    }
    button[kind="primary"]:hover, [data-testid="baseButton-primary"]:hover {
        background-color: #0ea5e9 !important;
        border-color: #0284c7 !important;
        color: #0f172a !important;
    }
    button[kind="primary"]:focus, [data-testid="baseButton-primary"]:focus {
        box-shadow: 0 0 0 0.2rem rgba(56, 189, 248, 0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 左右分欄：左側放狀態、目標按鈕、精簡版分析與操作按鈕，右側放選牌區、勝率結果與十強手牌
col_left, col_space, col_right = st.columns([1, 0.05, 2.2])

with col_left:
    st.subheader("⚙️ 遊戲模式設定")
    
    # 模式切換按鈕（單牌手 vs 兩個牌手 vs 三個牌手）
    mode_col1, mode_col2, mode_col3 = st.columns(3)
    with mode_col1:
        if st.button("👤 單牌手", type="primary" if st.session_state.game_mode == '單牌手模式' else "secondary", use_container_width=True):
            st.session_state.game_mode = '單牌手模式'
            if st.session_state.active_target in ['hero2', 'hero3']:
                st.session_state.active_target = 'hero'
            st.rerun()
    with mode_col2:
        if st.button("👥 兩個牌手", type="primary" if st.session_state.game_mode == '兩個牌手模式' else "secondary", use_container_width=True):
            st.session_state.game_mode = '兩個牌手模式'
            if st.session_state.active_target == 'hero3':
                st.session_state.active_target = 'hero'
            st.rerun()
    with mode_col3:
        if st.button("👨‍👦‍👦 三個牌手", type="primary" if st.session_state.game_mode == '三個牌手模式' else "secondary", use_container_width=True):
            st.session_state.game_mode = '三個牌手模式'
            st.rerun()

    st.markdown("---")
    st.subheader("🎯 選擇填入欄位")
    
    # 動態調整填入目標按鈕
    if st.session_state.game_mode == '三個牌手模式':
        t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)
        with t_col1:
            if st.button("1P", type="primary" if st.session_state.active_target == 'hero' else "secondary", use_container_width=True):
                st.session_state.active_target = 'hero'
                st.rerun()
        with t_col2:
            if st.button("2P", type="primary" if st.session_state.active_target == 'hero2' else "secondary", use_container_width=True):
                st.session_state.active_target = 'hero2'
                st.rerun()
        with t_col3:
            if st.button("3P", type="primary" if st.session_state.active_target == 'hero3' else "secondary", use_container_width=True):
                st.session_state.active_target = 'hero3'
                st.rerun()
        with t_col4:
            if st.button("對手", type="primary" if st.session_state.active_target == 'villain' else "secondary", use_container_width=True):
                st.session_state.active_target = 'villain'
                st.rerun()
        with t_col5:
            if st.button("公牌", type="primary" if st.session_state.active_target == 'board' else "secondary", use_container_width=True):
                st.session_state.active_target = 'board'
                st.rerun()
    elif st.session_state.game_mode == '兩個牌手模式':
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        with t_col1:
            if st.button("1P", type="primary" if st.session_state.active_target == 'hero' else "secondary", use_container_width=True):
                st.session_state.active_target = 'hero'
                st.rerun()
        with t_col2:
            if st.button("2P", type="primary" if st.session_state.active_target == 'hero2' else "secondary", use_container_width=True):
                st.session_state.active_target = 'hero2'
                st.rerun()
        with t_col3:
            if st.button("對手", type="primary" if st.session_state.active_target == 'villain' else "secondary", use_container_width=True):
                st.session_state.active_target = 'villain'
                st.rerun()
        with t_col4:
            if st.button("公牌", type="primary" if st.session_state.active_target == 'board' else "secondary", use_container_width=True):
                st.session_state.active_target = 'board'
                st.rerun()
    else:
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            if st.button("手牌", type="primary" if st.session_state.active_target == 'hero' else "secondary", use_container_width=True):
                st.session_state.active_target = 'hero'
                st.rerun()
        with t_col2:
            if st.button("對手", type="primary" if st.session_state.active_target == 'villain' else "secondary", use_container_width=True):
                st.session_state.active_target = 'villain'
                st.rerun()
        with t_col3:
            if st.button("公牌", type="primary" if st.session_state.active_target == 'board' else "secondary", use_container_width=True):
                st.session_state.active_target = 'board'
                st.rerun()
            
    st.markdown("---")
    st.subheader("📌 目前牌面狀態")
    
    def format_cards(cards):
        if not cards:
            return "*(尚未選擇)*"
        formatted = []
        suit_symbols = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
        for c in cards:
            rank, suit = c[0], c[1].lower()
            formatted.append(f"**{rank}{suit_symbols.get(suit, suit)}**")
        return "  ".join(formatted)

    if st.session_state.game_mode == '三個牌手模式':
        st.markdown(f"**1P 手牌**： {format_cards(st.session_state.hero_cards)}")
        st.markdown(f"**2P 手牌**： {format_cards(st.session_state.hero2_cards) if st.session_state.hero2_cards else '*(尚未選擇)*'}")
        st.markdown(f"**3P 手牌**： {format_cards(st.session_state.hero3_cards) if st.session_state.hero3_cards else '*(尚未選擇)*'}")
    elif st.session_state.game_mode == '兩個牌手模式':
        st.markdown(f"**1P 手牌**： {format_cards(st.session_state.hero_cards)}")
        st.markdown(f"**2P 手牌**： {format_cards(st.session_state.hero2_cards) if st.session_state.hero2_cards else '*(尚未選擇)*'}")
    else:
        st.markdown(f"**你的手牌**： {format_cards(st.session_state.hero_cards)}")
        
    st.markdown(f"**對手手牌**： {format_cards(st.session_state.villain_cards) if st.session_state.villain_cards else '*(未知/隨機)*'}")
    st.markdown(f"**目前公牌**： {format_cards(st.session_state.board_cards) if st.session_state.board_cards else '*(無/翻牌前)*'}")
    
    # 操作按鈕群組（回看上一把牌 & 清空重置）
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("🔄 回看上一把", use_container_width=True):
            if st.session_state.prev_hero_cards or st.session_state.prev_board_cards:
                temp_h, temp_h2, temp_h3, temp_v, temp_b = st.session_state.hero_cards, st.session_state.hero2_cards, st.session_state.hero3_cards, st.session_state.villain_cards, st.session_state.board_cards
                st.session_state.hero_cards = st.session_state.prev_hero_cards
                st.session_state.hero2_cards = st.session_state.prev_hero2_cards
                st.session_state.hero3_cards = st.session_state.prev_hero3_cards
                st.session_state.villain_cards = st.session_state.prev_villain_cards
                st.session_state.board_cards = st.session_state.prev_board_cards
                st.session_state.prev_hero_cards = temp_h
                st.session_state.prev_hero2_cards = temp_h2
                st.session_state.prev_hero3_cards = temp_h3
                st.session_state.prev_villain_cards = temp_v
                st.session_state.prev_board_cards = temp_b
                st.rerun()
            else:
                st.warning("尚無上一把紀錄！")
    with b_col2:
        if st.button("🗑️ 清空重置", use_container_width=True):
            if st.session_state.hero_cards or st.session_state.hero2_cards or st.session_state.hero3_cards or st.session_state.board_cards:
                st.session_state.prev_hero_cards = list(st.session_state.hero_cards)
                st.session_state.prev_hero2_cards = list(st.session_state.hero2_cards)
                st.session_state.prev_hero3_cards = list(st.session_state.hero3_cards)
                st.session_state.prev_villain_cards = list(st.session_state.villain_cards)
                st.session_state.prev_board_cards = list(st.session_state.board_cards)
            st.session_state.hero_cards = []
            st.session_state.hero2_cards = []
            st.session_state.hero3_cards = []
            st.session_state.villain_cards = []
            st.session_state.board_cards = []
            st.session_state.active_target = 'hero'
            st.rerun()

    # 精簡版「牌型與機率分析」
    st.markdown("---")
    st.subheader("🃏 牌型與機率預測")
    
    if len(st.session_state.hero_cards) != 2:
        st.info("💡 請先選好 2 張手牌")
    else:
        evaluator = Evaluator()
        hero_c = [Card.new(s) for s in st.session_state.hero_cards]
        board_c = [Card.new(s) for s in st.session_state.board_cards] if st.session_state.board_cards else []
        
        # 1. 當前成牌顯示
        if len(board_c) >= 3:
            all_cards = hero_c + board_c
            if len(all_cards) <= 7:
                best_score = 9999
                best_class_str = ""
                for combo in combinations(all_cards, 5):
                    score = evaluator.evaluate(list(combo), [])
                    if score < best_score:
                        best_score = score
                        class_int = evaluator.get_rank_class(score)
                        best_class_str = evaluator.class_to_string(class_int)
                st.success(f"🔥 當前：**{best_class_str}**")
        else:
            st.caption("ℹ️ 公牌達 3 張以上時顯示目前成牌")
            
        # 2. 未來牌型機率
        if len(board_c) < 5:
            with st.spinner("計算中..."):
                cards_to_come = 5 - len(board_c)
                simulations = 1500
                hand_counts = {
                    "高牌": 0, "一対": 0, "兩對": 0,
                    "三條": 0, "順子": 0, "同花": 0,
                    "葫蘆": 0, "四條": 0, "同花順": 0
                }
                
                mapping = {
                    "High Card": "高牌", "Pair": "一對", "Two Pair": "兩對",
                    "Three of a Kind": "三條", "Straight": "順子", "Flush": "同花",
                    "Full House": "葫蘆", "Four of a Kind": "四條",
                    "Straight Flush": "同花順", "Royal Flush": "同花順"
                }
                
                for _ in range(simulations):
                    deck = Deck()
                    used = hero_c + board_c
                    for c in used:
                        if c in deck.cards:
                            deck.cards.remove(c)
                            
                    runout = deck.draw(cards_to_come)
                    full_board = board_c + runout
                    all_7 = hero_c + full_board
                    
                    best_score = 9999
                    best_cat = ""
                    for combo in combinations(all_7, 5):
                        score = evaluator.evaluate(list(combo), [])
                        if score < best_score:
                            best_score = score
                            cat_name = evaluator.class_to_string(evaluator.get_rank_class(score))
                            best_cat = mapping.get(cat_name, cat_name)
                    
                    if best_cat in hand_counts:
                        hand_counts[best_cat] += 1
                
                filtered_counts = {k: v for k, v in hand_counts.items() if v > 0}
                items = list(filtered_counts.items())
                
                st.caption("📊 未來最終成牌機率：")
                for i in range(0, len(items), 2):
                    c1, c2 = st.columns(2)
                    with c1:
                        k1, cnt1 = items[i]
                        pct1 = (cnt1 / simulations) * 100
                        if pct1 >= 0.5:
                            st.text(f"{k1}: {pct1:.1f}%")
                    if i + 1 < len(items):
                        with c2:
                            k2, cnt2 = items[i+1]
                            pct2 = (cnt2 / simulations) * 100
                            if pct2 >= 0.5:
                                st.text(f"{k2}: {pct2:.1f}%")

with col_right:
    st.subheader("🎴 點擊選牌（選中會變成天藍色，再點一次可取消）")
    
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits_info = [
        ('s', '♠'), 
        ('h', '♥'), 
        ('d', '♦'), 
        ('c', '♣')
    ]
    
    for suit_key, suit_symbol in suits_info:
        cols = st.columns(13)
        for i, rank in enumerate(ranks):
            card_str = rank + suit_key
            
            is_in_hero = card_str in st.session_state.hero_cards
            is_in_hero2 = card_str in st.session_state.hero2_cards
            is_in_hero3 = card_str in st.session_state.hero3_cards
            is_in_villain = card_str in st.session_state.villain_cards
            is_in_board = card_str in st.session_state.board_cards
            
            if st.session_state.game_mode == '三個牌手模式':
                is_picked = is_in_hero or is_in_hero2 or is_in_hero3 or is_in_villain or is_in_board
            elif st.session_state.game_mode == '兩個牌手模式':
                is_picked = is_in_hero or is_in_hero2 or is_in_villain or is_in_board
            else:
                is_picked = is_in_hero or is_in_villain or is_in_board
            
            btn_type = "primary" if is_picked else "secondary"
            
            with cols[i]:
                if st.button(f"{rank}{suit_symbol}", key=f"btn_{card_str}", type=btn_type, use_container_width=True):
                    if is_picked:
                        if is_in_hero: st.session_state.hero_cards.remove(card_str)
                        if is_in_hero2: st.session_state.hero2_cards.remove(card_str)
                        if is_in_hero3: st.session_state.hero3_cards.remove(card_str)
                        if is_in_villain: st.session_state.villain_cards.remove(card_str)
                        if is_in_board: st.session_state.board_cards.remove(card_str)
                    else:
                        target = st.session_state.active_target
                        if target == 'hero' and len(st.session_state.hero_cards) < 2:
                            st.session_state.hero_cards.append(card_str)
                        elif target == 'hero2' and len(st.session_state.hero2_cards) < 2:
                            st.session_state.hero2_cards.append(card_str)
                        elif target == 'hero3' and len(st.session_state.hero3_cards) < 2:
                            st.session_state.hero3_cards.append(card_str)
                        elif target == 'villain' and len(st.session_state.villain_cards) < 2:
                            st.session_state.villain_cards.append(card_str)
                        elif target == 'board' and len(st.session_state.board_cards) < 5:
                            st.session_state.board_cards.append(card_str)
                    st.rerun()

    st.markdown("---")
    
    # 模擬次數與即時勝率維持在右側下方
    num_simulations = st.slider("模擬次數", min_value=1000, max_value=30000, value=10000, step=1000)
    
    # 將右下方改為左右兩欄：左側放即時勝率分析，右側放前 10 手起手牌
    bottom_col1, bottom_col2 = st.columns([1, 1])
    
    with bottom_col1:
        st.subheader("📊 即時勝率分析")
        if len(st.session_state.hero_cards) != 2:
            st.info("💡 請先在左側選好 2 張手牌")
        else:
            with st.spinner("⚡ 計算中..."):
                evaluator = Evaluator()
                try:
                    hero_cards = [Card.new(s) for s in st.session_state.hero_cards]
                    hero2_cards = [Card.new(s) for s in st.session_state.hero2_cards] if len(st.session_state.hero2_cards) == 2 else None
                    hero3_cards = [Card.new(s) for s in st.session_state.hero3_cards] if len(st.session_state.hero3_cards) == 2 else None
                    villain_cards = [Card.new(s) for s in st.session_state.villain_cards] if st.session_state.villain_cards else None
                    board = [Card.new(s) for s in st.session_state.board_cards] if st.session_state.board_cards else []
                    
                    hero_wins = 0
                    hero2_wins = 0
                    hero3_wins = 0
                    villain_wins = 0
                    ties = 0
                    
                    is_three_mode = (st.session_state.game_mode == '三個牌手模式' and hero2_cards is not None and hero3_cards is not None)
                    is_two_players_mode = (st.session_state.game_mode == '兩個牌手模式' and hero2_cards is not None)
                    
                    for _ in range(num_simulations):
                        deck = Deck()
                        used_cards = hero_cards + board
                        if is_two_players_mode or is_three_mode:
                            used_cards += hero2_cards
                        if is_three_mode:
                            used_cards += hero3_cards
                        if villain_cards:
                            used_cards += villain_cards
                            
                        for card in used_cards:
                            if card in deck.cards:
                                deck.cards.remove(card)
                            
                        current_hero2_cards = hero2_cards
                        if (is_two_players_mode or is_three_mode) and current_hero2_cards is None:
                            current_hero2_cards = deck.draw(2)
                            
                        current_hero3_cards = hero3_cards
                        if is_three_mode and current_hero3_cards is None:
                            current_hero3_cards = deck.draw(2)
                            
                        current_villain_cards = villain_cards
                        if not current_villain_cards:
                            current_villain_cards = deck.draw(2)
                            
                        cards_needed = 5 - len(board)
                        runout = deck.draw(cards_needed)
                        current_board = board + runout
                        
                        hero_score = evaluator.evaluate(current_board, hero_cards)
                        villain_score = evaluator.evaluate(current_board, current_villain_cards)
                        
                        if is_three_mode:
                            h2_score = evaluator.evaluate(current_board, current_hero2_cards)
                            h3_score = evaluator.evaluate(current_board, current_hero3_cards)
                            best_score = min(hero_score, h2_score, h3_score, villain_score)
                            
                            h_win = (hero_score == best_score)
                            h2_win = (h2_score == best_score)
                            h3_win = (h3_score == best_score)
                            v_win = (villain_score == best_score)
                            
                            # 若只有一方拿到最佳分數則計為贏，多人同分則視為平手
                            if h_win and not h2_win and not h3_win and not v_win:
                                hero_wins += 1
                            elif h2_win and not h_win and not h3_win and not v_win:
                                hero2_wins += 1
                            elif h3_win and not h_win and not h2_win and not v_win:
                                hero3_wins += 1
                            elif v_win and not h_win and not h2_win and not h3_win:
                                villain_wins += 1
                            else:
                                ties += 1
                        elif is_two_players_mode:
                            h2_score = evaluator.evaluate(current_board, current_hero2_cards)
                            best_score = min(hero_score, h2_score, villain_score)
                            
                            h_win = (hero_score == best_score)
                            h2_win = (h2_score == best_score)
                            v_win = (villain_score == best_score)
                            
                            if h_win and not h2_win and not v_win:
                                hero_wins += 1
                            elif h2_win and not h_win and not v_win:
                                hero2_wins += 1
                            elif v_win and not h_win and not h2_win:
                                villain_wins += 1
                            else:
                                ties += 1
                        else:
                            if hero_score < villain_score:
                                hero_wins += 1
                            elif hero_score > villain_score:
                                villain_wins += 1
                            else:
                                ties += 1
                            
                    total_players = 4 if is_three_mode else (3 if is_two_players_mode else 2)
                    equity = (hero_wins + (ties / total_players)) / num_simulations * 100
                    
                    if is_three_mode:
                        equity2 = (hero2_wins + (ties / 4)) / num_simulations * 100
                        equity3 = (hero3_wins + (ties / 4)) / num_simulations * 100
                        st.metric(label="1P 勝率 (Equity)", value=f"{equity:.2f}%")
                        st.metric(label="2P 勝率 (Equity)", value=f"{equity2:.2f}%")
                        st.metric(label="3P 勝率 (Equity)", value=f"{equity3:.2f}%")
                        st.markdown(f"**詳細數據**：1P勝: `{hero_wins}` | 2P勝: `{hero2_wins}` | 3P勝: `{hero3_wins}` | 對手勝: `{villain_wins}` | 平手: `{ties}`", unsafe_allow_html=True)
                    elif is_two_players_mode:
                        equity2 = (hero2_wins + (ties / 3)) / num_simulations * 100
                        st.metric(label="1P 勝率 (Equity)", value=f"{equity:.2f}%")
                        st.metric(label="2P 勝率 (Equity)", value=f"{equity2:.2f}%")
                        st.markdown(f"**詳細數據**：1P勝: `{hero_wins}` | 2P勝: `{hero2_wins}` | 對手勝: `{villain_wins}` | 平手: `{ties}`", unsafe_allow_html=True)
                    else:
                        st.metric(label="您的勝率 (Equity)", value=f"{equity:.2f}%")
                        st.markdown(f"**詳細數據**：勝場: `{hero_wins}` | 敗場: `{villain_wins}` | 平手: `{ties}`", unsafe_allow_html=True)
                    
                    # 行動建議
                    st.markdown("---")
                    st.markdown("##### 💡 智慧行動建議")
                    if equity >= 70:
                        st.success("🔥 **強烈建議：All-in / 加注 (Raise)**\n\n勝率極高！建議主動施壓、擴大底池，賺取最大價值。")
                    elif equity >= 50:
                        st.info("⚖️ **建議：跟注 (Call) 或小額加注**\n\n勝率具備優勢，適合穩健跟注或依據對手風格進行價值下注。")
                    elif equity >= 35:
                        st.warning("⚠️ **建議：謹慎跟注 (Call) / 視賠率決定**\n\n勝率一般，若對手下注過大（籌碼風險高）建議考慮棄牌；若底池賠率好可拼聽牌。")
                    else:
                        st.error("❌ **建議：棄牌 (Fold) / 避免硬拼**\n\n目前勝率偏低，盲目跟注或 All-in 長期來看虧損機率高。")
                        
                except Exception as e:
                    st.error(f"❌ 錯誤: {e}")

    with bottom_col2:
        st.subheader("🏆 勝率最高前 10 手起手牌")
        st.caption("對戰隨機單一對手之平均歐印勝率參考：")
        
        top_hands = [
            ("A-A (對子)", "約 85%"),
            ("K-K (對子)", "約 82%"),
            ("Q-Q (對子)", "約 80%"),
            ("J-J (對子)", "約 77%"),
            ("A-K (同花)", "約 67%"),
            ("T-T (對子)", "約 74%"),
            ("A-K (雜色)", "約 65%"),
            ("A-Q (同花)", "約 66%"),
            ("A-J (同花)", "約 65%"),
            ("9-9 (對子)", "約 71%")
        ]
        
        tc1, tc2 = st.columns(2)
        for idx, (h, p) in enumerate(top_hands):
            target_col = tc1 if idx < 5 else tc2
            with target_col:
                st.text(f"{idx+1}. {h} : {p}")
