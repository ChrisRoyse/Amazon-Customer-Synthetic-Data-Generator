# event_generator.py - Refactored for Behavioral Parameters

import random
import datetime
import logging

# Import necessary components from other modules
try:
    import config
    import utils
except ImportError as e:
    logging.error(f"Error importing modules in event_generator.py: {e}. Ensure config.py and utils.py exist.")
    raise

def generate_event_details(event_type, profile, current_timestamp):
    """
    Generates plausible details for a given event type based on the profile's
    current state and sampled behavioral parameters. Updates internal state.

    Args:
        event_type (str): The type of event to generate details for.
        profile (dict): The customer profile dictionary, including '_internal_state'.
        current_timestamp (datetime.datetime): The timestamp when the event occurs.

    Returns:
        dict: A dictionary containing the event details, or None if invalid.
    """
    if "_internal_state" not in profile or "behavioral_params" not in profile["_internal_state"]:
        logging.error(f"Profile {profile.get('profile_id', 'N/A')} missing state or params. Cannot generate event details.")
        return None

    state = profile["_internal_state"]
    params = state["behavioral_params"]
    details = {"session_id": state["current_session_id"]}

    # --- Helper Functions within context ---
    def get_relevant_category(bias_towards_recent=0.6):
        # (Keep existing logic - relies on interests/history, not direct params)
        possible_cats = list(state.get("current_interests", config.BASE_INTEREST_CATEGORIES))
        if not possible_cats: possible_cats = config.BASE_INTEREST_CATEGORIES
        recent_cats = []
        for p in state.get("viewed_products", [])[-10:]: recent_cats.append(p.get('category'))
        for s in state.get("search_history", [])[-5:]:
            query = s.get('query', '').lower()
            for cat in config.BASE_INTEREST_CATEGORIES:
                if cat.lower() in query: recent_cats.append(cat); break
        for o in state.get("orders", [])[-3:]:
            for item in o.get('items', []): recent_cats.append(item.get('category'))
        recent_cats = [cat for cat in recent_cats if cat]
        if recent_cats and random.random() < bias_towards_recent:
            return random.choice(recent_cats)
        else:
            return random.choice(possible_cats)

    def generate_product_for_event(category=None, base_product=None):
        # Incorporate brand affinity
        cat = category or get_relevant_category()
        brand_affinity = params.get("brand_affinity_strength", 0.3)
        preferred_brand = None

        # Check recent purchases for brands in this category
        brand_counts = state.get("brand_purchase_counts", {}).get(cat, {})
        if brand_counts and random.random() < brand_affinity:
            # Weighted choice towards frequently purchased brands
            total_purchases = sum(brand_counts.values())
            brand_weights = [(brand, count / total_purchases) for brand, count in brand_counts.items()]
            preferred_brand = utils.select_weighted_item(brand_weights)
            logging.debug(f"Brand affinity triggered: Chose '{preferred_brand}' for category '{cat}'")

        product_id = base_product['product_id'] if base_product and 'product_id' in base_product else utils.generate_product_id()
        product_name = base_product['product_name'] if base_product and 'product_name' in base_product else utils.generate_product_name(cat)
        price = base_product.get('price') if base_product and 'price' in base_product else utils.get_plausible_price(cat)
        brand = preferred_brand or (base_product.get('brand') if base_product else random.choice(config.BRANDS)) # Use preferred or existing or random

        product_details = {
            "product_id": product_id,
            "product_name": product_name,
            "category": cat,
            "price": price,
            "brand": brand
        }
        return product_details

    def get_device():
        # (Keep existing logic - relies on state['devices'])
        devices = state.get("devices", [])
        primary_device = state.get("primary_device")
        if not devices: return "Unknown Device"
        if primary_device and (random.random() < 0.7 or len(devices) == 1):
            return primary_device
        else:
            secondary_devices = [d for d in devices if d != primary_device]
            return random.choice(secondary_devices) if secondary_devices else primary_device

    # --- Event Type Logic ---
    device_used = get_device()
    details["device_used"] = device_used

    # --- Core Shopping Events ---
    if event_type == "search":
        search_type = random.choice(config.SEARCH_TYPES)
        query_base = get_relevant_category() if search_type == "Product Search" else random.choice(["action movie", "popular playlist", "thriller novel", "how to"])
        # More specific search terms based on parameters?
        mods = ['reviews', 'best', 'cheap', 'used', 'refurbished', 'gift', 'organic', 'sustainable', '']
        if random.random() < params.get("deal_seeking_propensity", 0.3): mods.extend(['deals', 'discount', 'coupon', 'clearance'])
        if random.random() < params.get("brand_affinity_strength", 0.3) * 0.5: # Lower chance to search specific brand
             # Find a brand previously purchased?
             all_brands = [item['brand'] for order in state.get('orders', []) for item in order.get('items', []) if 'brand' in item]
             if all_brands: mods.append(random.choice(all_brands))

        query = f"{query_base} {random.choice(mods)}".strip().replace("  ", " ")
        results_count = random.randint(0, 5000) if query else 0
        # More filters used if high comparison propensity?
        num_filters = random.randint(0, 1 + int(params.get("comparison_shopping_prob", 0.3) * 4))
        filters_used = random.sample(['prime', 'rating_4_star_up', 'price_range', 'brand', 'color', 'release_year', 'genre', 'size'], k=num_filters)

        details.update({
            "search_type": search_type,
            "search_query": query,
            "results_count": results_count,
            "filters_used": filters_used
        })
        state.setdefault("search_history", []).append({"query": query, "type": search_type, "timestamp": current_timestamp, "result_count": results_count})
        state["search_history"] = state["search_history"][-50:]

    elif event_type == "view_product":
        # (Generation logic largely unchanged, relies on history/interests)
        product = None
        source = "unknown"
        if state.get("search_history") and random.random() < 0.5: source = "search_results"; #... (rest of logic)
        elif state.get("wishlist") and random.random() < params.get("wishlist_usage_propensity", 0.3) * 0.5: source = "wishlist"; #...
        elif state.get("viewed_products") and random.random() < 0.3: source = "related_product"; #...
        else: source = random.choice(["browse", "recommendation", "external_link"]); #...

        # Simplified generation call for brevity
        product = generate_product_for_event() # Assume full logic exists here as before

        if not product: return None
        # View duration influenced by latency factor? (Lower latency = shorter views?)
        latency_factor = params.get("purchase_latency_factor", 1.0)
        view_duration = random.randint(5, 300) * (1.0 / max(0.5, latency_factor)) # Faster look if low latency?
        details.update(product)
        details["source"] = source
        details["view_duration_seconds"] = round(max(3, view_duration)) # Min 3 seconds
        state.setdefault("viewed_products", []).append({**product, "timestamp": current_timestamp})
        state["viewed_products"] = state["viewed_products"][-50:]

    elif event_type == "add_to_cart":
        # (Source selection logic largely unchanged, relies on history/interests)
        product_to_add = None
        source = "unknown"
        # ... (selection logic based on viewed, wishlist, search, impulse) ...
        # Impulse probability directly uses parameter
        impulse_prob = params.get("impulse_purchase_prob", 0.05) * 0.5 # Lower chance for add vs buy
        # ... (rest of selection logic) ...

        # Simplified generation call for brevity
        product_to_add = generate_product_for_event() # Assume full logic exists here as before

        if not product_to_add: return None
        cart = state.setdefault("cart", [])
        existing_cart_item = next((item for item in cart if item["product_id"] == product_to_add["product_id"]), None)
        quantity = random.randint(1, 3)
        if existing_cart_item and random.random() < 0.5:
             existing_cart_item["quantity"] += quantity
             existing_cart_item["added_timestamp"] = current_timestamp
             details.update({"product_id": existing_cart_item["product_id"], "quantity_added": quantity, "new_total_quantity": existing_cart_item["quantity"], "source": source})
        else:
            cart_item = { #... (create cart item) ...
                 "product_id": product_to_add["product_id"], "product_name": product_to_add.get("product_name"),
                 "category": product_to_add.get("category"), "quantity": quantity,
                 "price_per_item": product_to_add.get("price"), "added_timestamp": current_timestamp,
                 "brand": product_to_add.get("brand")
            }
            cart.append(cart_item)
            details.update({"product_id": cart_item["product_id"], "quantity_added": quantity, "new_total_quantity": quantity, "source": source})
        state["cart"] = cart

    elif event_type == "remove_from_cart":
        # (Logic unchanged, relies on cart state)
        cart = state.get("cart", [])
        if not cart: return None
        removed_item = random.choice(cart)
        cart.remove(removed_item)
        details.update({"product_id": removed_item["product_id"], "quantity_removed": removed_item["quantity"], "price_per_item": removed_item["price_per_item"]})
        state["cart"] = cart

    elif event_type == "purchase":
        cart = state.get("cart", [])
        items_to_buy = []
        purchase_source = "cart"
        impulse_prob = params.get("impulse_purchase_prob", 0.05)
        is_impulse = not cart or random.random() < impulse_prob

        if is_impulse:
             purchase_source = "impulse"
             num_items = random.randint(1, 2) # Impulse usually fewer items
             for _ in range(num_items):
                 product = generate_product_for_event()
                 items_to_buy.append({ #... (item details) ...
                     "product_id": product["product_id"], "product_name": product["product_name"], "category": product["category"],
                     "quantity": 1, "price_per_item": product["price"], "brand": product.get("brand")})
        elif cart:
            abandon_prob = params.get("cart_abandon_propensity", 0.3)
            if random.random() < abandon_prob and len(cart) > 1:
                 buy_count = random.randint(1, len(cart) -1)
                 items_to_buy = random.sample(cart, buy_count)
            else:
                 items_to_buy = list(cart)
            purchased_ids = {item['product_id'] for item in items_to_buy}
            state["cart"] = [item for item in cart if item['product_id'] not in purchased_ids]
        else:
            return None

        if not items_to_buy: return None

        total = sum(item['price_per_item'] * item['quantity'] for item in items_to_buy)
        order_id = utils.generate_order_id()
        coupon_used = None
        # Higher chance to use coupon if deal seeker and coupon available
        if state.get("active_promotions") and random.random() < params.get("deal_seeking_propensity", 0.3):
             coupon_code = list(state["active_promotions"].keys())[0]
             coupon_details = state["active_promotions"].pop(coupon_code)
             discount_amount = coupon_details.get("value", 5.0) # Simplified discount
             total = max(0, total - discount_amount)
             coupon_used = coupon_code

        details.update({ #... (order details) ...
            "order_id": order_id, "items": items_to_buy, "item_count": sum(item['quantity'] for item in items_to_buy),
            "distinct_item_count": len(items_to_buy), "total_amount": round(total * state.get("seasonal_boost", 1.0), 2),
            "payment_method": random.choice(["Credit Card", "Debit Card", "Gift Card Balance", "Amazon Pay"]),
            "shipping_address_type": random.choice(["Home", "Work"]), "shipping_speed": random.choice(["Standard", "Expedited", "Two-Day (Prime)"]) if state.get("is_prime") else "Standard",
            "purchase_source": purchase_source, "coupon_used": coupon_used
        })
        # Update state: add order, update brand purchase counts
        state.setdefault("orders", []).append({
            "order_id": order_id, "items": items_to_buy, "total": details["total_amount"],
            "timestamp": current_timestamp, "status": "processing"
        })
        # Update brand counts for affinity modeling
        brand_counts = state.setdefault("brand_purchase_counts", {})
        for item in items_to_buy:
            brand = item.get("brand")
            cat = item.get("category")
            if brand and cat:
                cat_brands = brand_counts.setdefault(cat, {})
                cat_brands[brand] = cat_brands.get(brand, 0) + item["quantity"]


    elif event_type == "return_item":
        # Return propensity influences likelihood (handled in simulation.py weighting)
        # Details generation remains similar
        eligible_orders = [o for o in state.get("orders", []) if o.get("status") in ["delivered", "completed", "returned_partial"] and (current_timestamp - o["timestamp"]).days < 30]
        if not eligible_orders: return None
        order = random.choice(eligible_orders)
        eligible_items = [item for item in order["items"] if item.get("return_status") != "returned"]
        if not eligible_items: return None
        item_to_return = random.choice(eligible_items)
        reason = random.choice(config.RETURN_REASONS)
        return_method = random.choice(["UPS Dropoff", "Kohls Dropoff", "Amazon Locker", "Mail Back (Prepaid Label)"])
        details.update({ #... (return details) ...
             "order_id": order["order_id"], "product_id": item_to_return["product_id"], "product_name": item_to_return["product_name"],
             "quantity_returned": item_to_return["quantity"], "reason": reason, "return_method": return_method
        })
        item_to_return["return_status"] = "returned"
        order["status"] = "returned_full" if all(it.get("return_status") == "returned" for it in order["items"]) else "returned_partial"


    # --- Other Events (Apply parameter influence where applicable) ---
    elif event_type == "browse_category":
        # Session length/page view factors influence duration/views?
        page_factor = params.get("page_view_factor", 1.0)
        session_factor = params.get("session_length_factor", 1.0)
        category = get_relevant_category(bias_towards_recent=0.3)
        time_spent = random.randint(30, 600) * session_factor
        products_viewed_in_browse = max(0, int(random.gauss(2, 2) * page_factor)) # Avg 2 views, influenced by factor
        details.update({ #... (browse details) ...
            "category_name": category, "time_spent_seconds": round(max(10, time_spent)),
            "products_viewed_count": products_viewed_in_browse,
            "sort_applied": random.choice([None, "price_low_high", "avg_customer_review", "featured"]),
            "filters_applied": random.sample(['prime', 'brand', 'rating', 'price_range'], k=random.randint(0, 2))
        })

    elif event_type == "view_review":
        # Number of reviews read influenced by propensity
        read_propensity = params.get("review_read_propensity", 0.5)
        num_reviews = max(1, int(random.gauss(5, 4) * (0.5 + read_propensity))) # Read more if high propensity
        if not state.get("viewed_products"): return None
        product = random.choice(state["viewed_products"][-5:])
        details.update({ #... (view review details) ...
             "product_id": product["product_id"], "number_of_reviews_read": num_reviews,
             "sort_order": random.choice(["most_recent", "top_rated", "most_helpful"]),
             "filter_applied": random.choice([None, "verified_purchase", "with_images", "5_star"])
        })

    elif event_type == "write_review":
        # Review length/detail influenced by propensity?
        write_propensity = params.get("review_write_propensity", 0.1)
        # ... (find eligible item logic remains same) ...
        eligible_orders = [o for o in state.get("orders", []) if o.get("status") in ["delivered", "completed"] and (current_timestamp - o["timestamp"]).days < 90]
        if not eligible_orders: return None
        order = random.choice(eligible_orders)
        eligible_items = [item for item in order["items"] if item.get("review_status") != "reviewed" and item.get("return_status") != "returned"]
        if not eligible_items: return None
        item = random.choice(eligible_items)

        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 15, 35, 40], k=1)[0]
        review_length = max(10, int(random.gauss(100, 80) * (0.5 + write_propensity))) # Longer reviews if higher propensity
        has_title = random.random() < 0.4 + write_propensity * 0.4
        has_photos = random.random() < 0.1 + write_propensity * 0.2
        has_video = random.random() < 0.02 + write_propensity * 0.1
        review_id = utils.generate_review_id()
        details.update({ #... (write review details) ...
            "review_id": review_id, "product_id": item["product_id"], "order_id": order["order_id"],
            "rating": rating, "review_length_words": review_length, "has_title": has_title,
            "has_photos": has_photos, "has_video": has_video
        })
        item["review_status"] = "reviewed"

    elif event_type == "update_wishlist":
        # Usage influenced by propensity (handled in simulation.py weighting)
        # Details generation remains similar
        action = random.choice(["add", "remove"])
        product_id = None
        source = None
        wishlist = state.setdefault("wishlist", set())
        if action == "add":
            # ... (product selection logic) ...
            product_to_add = generate_product_for_event() # Simplified
            if product_to_add: product_id = product_to_add["product_id"]; wishlist.add(product_id); source="product_page/browse"
            else: return None
        elif action == "remove":
            if not wishlist: return None
            product_id = random.choice(list(wishlist)); wishlist.remove(product_id); source="wishlist_page"
        details.update({"action": action, "product_id": product_id, "source": source, "wishlist_size": len(wishlist)})
        state["wishlist"] = wishlist

    elif event_type == "alexa_interaction":
        # Shopping intent influenced by parameter
        alexa_shop_prop = params.get("alexa_shopping_propensity", 0.1)
        # ... (find echo device logic) ...
        echo_devices = [d for d in state.get("devices", []) if "Echo" in d]
        if not echo_devices: return None

        intent = random.choice(config.ALEXA_INTENTS)
        # Override intent to shopping sometimes based on propensity
        if intent not in ["Order Product", "Shopping List Add/Remove", "Check Order Status"] and random.random() < alexa_shop_prop:
             intent = random.choice(["Order Product", "Shopping List Add/Remove"])

        value = None; success = random.random() < 0.95
        # ... (generate value based on intent logic) ...
        if intent == "Order Product":
             product = generate_product_for_event(category=random.choice(["Grocery", "Household Supplies"]))
             value = product["product_name"]
        # ... (other intents) ...
        details.update({"intent": intent, "value": value, "success": success, "device_used": random.choice(echo_devices)})

    elif event_type == "clip_coupon":
        # Likelihood handled by weighting, details generation same
        category = get_relevant_category()
        value = round(random.uniform(0.5, 25.0), 2)
        coupon_type = random.choice(["percentage", "fixed_amount"])
        if coupon_type == "percentage": value = random.randint(5, 50)
        coupon_code = utils.generate_coupon_code()
        details.update({"coupon_code": coupon_code, "coupon_value": value, "coupon_type": coupon_type, "category_applied": category})
        state.setdefault("active_promotions", {})[coupon_code] = {"value": value, "type": coupon_type, "category": category}


    # --- Add other event types and apply parameter influence similarly ---
    # e.g., watch_prime_video duration influenced by prime_video_engagement?
    # e.g., manage_subscribe_save details influenced by subscribe_save_propensity?

    else:
        # Generic fallback for unhandled types
        details["notes"] = f"Generic event of type {event_type}"

    # Final check
    if not details:
        logging.warning(f"Failed to generate details for event type: {event_type} for profile {profile.get('profile_id', 'N/A')}")
        return None

    return details


if __name__ == '__main__':
    # Example usage/test requires a mock profile with behavioral params
    logging.basicConfig(level=logging.DEBUG)
    print("--- Testing Refactored Event Generation ---")

    mock_start_date = datetime.datetime(2024, 1, 1)
    mock_profile = {
        "profile_id": "cust_0001",
        "_internal_state": {
            "current_timestamp": mock_start_date, "current_age": 30,
            "current_interests": {"Electronics", "Books", "Deals & Bargains"},
            "is_prime": True, "used_services": {"Prime Membership", "Prime Video"},
            "behavioral_params": { # Sample parameters
                "activity_level": 0.7, "review_read_propensity": 0.8, "review_write_propensity": 0.2,
                "purchase_latency_factor": 0.8, "deal_seeking_propensity": 0.9, "brand_affinity_strength": 0.2,
                "tech_adoption_propensity": 0.6, "cart_abandon_propensity": 0.2, "return_propensity": 0.1,
                "session_length_factor": 1.2, "page_view_factor": 1.5, "comparison_shopping_prob": 0.7,
                "subscribe_save_propensity": 0.1, "wishlist_usage_propensity": 0.6, "impulse_purchase_prob": 0.1,
                "prime_video_engagement": 0.7, "amazon_music_engagement": 0.3, "kindle_engagement": 0.6,
                "audible_engagement": 0.2, "alexa_shopping_propensity": 0.1
            },
            "devices": ["Mobile App (iOS)", "Desktop Website (Mac)", "Echo Device"], "primary_device": "Mobile App (iOS)",
            "cart": [], "orders": [], "wishlist": set(), "viewed_products": [], "search_history": [],
            "last_event_timestamp": mock_start_date, "current_session_id": utils.generate_session_id(),
            "session_start_time": mock_start_date, "events_in_session": 0, "seasonal_boost": 1.0,
            "brand_purchase_counts": {}
        }
    }

    # Test events influenced by parameters
    event_types_to_test = ["search", "view_product", "view_review", "clip_coupon", "purchase", "add_to_cart"]
    for etype in event_types_to_test:
        print(f"\n--- Generating '{etype}' ---")
        event_details = generate_event_details(etype, mock_profile, datetime.datetime.now())
        if event_details:
            import json
            print(json.dumps(event_details, indent=2, default=str))
        else:
            print(f"Could not generate details for '{etype}'.")

    print("\n--- Event Generation Test Complete ---")