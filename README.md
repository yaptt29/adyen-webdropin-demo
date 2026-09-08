

# DEMO of Adyen Web Drop-in Checkout

---


A lightweight, scalable e-commerce checkout integration built with Flask (Python) and the Adyen Checkout SDK. This project demonstrates end-to-end payment processing using Adyen's Sessions Flow, multi-region dynamic localization, dynamic payment method blocking, real-time admin monitoring, and asynchronous webhook lifecycle handling.

🌟 Key Architectural Features
Adyen Sessions Flow Integration: Secure, PCI-compliant payment initialization using Adyen's modern Web Drop-in SDK.

Global Scale, Local Sale (Localization): Dynamic region switching supporting Europe (EUR/NL), Singapore (SGD/SG), and Australia (AUD/AU), allowing Adyen to automatically surface regional Local Payment Methods (LPMs).

Payment Method Filtering: Demonstrates programmatic risk and business logic using the blockedPaymentMethods configuration.

Asynchronous Webhook Event Handling: Event-driven order status updates (Pending Webhook ⏳ ➔ Authorised ✅ / Refused ❌) driven by incoming push notifications.

Merchant Back-Office Portal: Live auto-refreshing dashboard (/admin) to track real-time transaction statuses and pspReference identifiers.
