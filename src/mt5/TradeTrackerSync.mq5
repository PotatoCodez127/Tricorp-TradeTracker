//+------------------------------------------------------------------+
//|                                             TradeTrackerSync.mq5 |
//|                                            TriCorp TradeTracker  |
//+------------------------------------------------------------------+
#property copyright "TriCorp"
#property link      "https://your-dashboard.com"
#property version   "1.00"
#property strict

// Input for the user's unique dashboard ID or API key
input string InpUserToken = "USER_SECRET_TOKEN_123"; 
input string InpWebhookURL = "http://127.0.0.1:8000/api/webhook";

int OnInit() {
   // Run the sync every 60 seconds
   EventSetTimer(60); 
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) {
   EventKillTimer();
}

void OnTimer() {
   SyncTrades();
}

void SyncTrades() {
   // Get history for the last 30 days
   datetime to_date = TimeCurrent();
   datetime from_date = to_date - (30 * 24 * 60 * 60); 
   
   if(!HistorySelect(from_date, to_date)) {
      Print("Failed to load history.");
      return;
   }
   
    int deals_total = HistoryDealsTotal();
    Print("Processing ", deals_total, " deals for Account ", AccountInfoInteger(ACCOUNT_LOGIN));
    
    if(deals_total == 0) {
       Print("No closed deals found in last 30 days");
       return;
    }
    
    string json_deals = "[";
    bool first = true;
    
    for(int i = 0; i < deals_total; i++) {
      ulong deal_ticket = HistoryDealGetTicket(i);
      long deal_type = HistoryDealGetInteger(deal_ticket, DEAL_TYPE);
      
      // Only care about Buy (0) and Sell (1) deals that resulted in profit/loss (deal entry out)
      long deal_entry = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
      if((deal_type == DEAL_TYPE_BUY || deal_type == DEAL_TYPE_SELL) && deal_entry == DEAL_ENTRY_OUT) {
         
         if(!first) json_deals += ",";
         
         string symbol = HistoryDealGetString(deal_ticket, DEAL_SYMBOL);
         double volume = HistoryDealGetDouble(deal_ticket, DEAL_VOLUME);
         double profit = HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
         double price = HistoryDealGetDouble(deal_ticket, DEAL_PRICE);
         long time = HistoryDealGetInteger(deal_ticket, DEAL_TIME);
         
         // Simple JSON string building
         json_deals += StringFormat(
            "{\"ticket\":%llu,\"symbol\":\"%s\",\"type\":\"%s\",\"volume\":%.2f,\"profit\":%.2f,\"price\":%.5f,\"time\":%lld}",
            deal_ticket, symbol, (deal_type == 0 ? "BUY" : "SELL"), volume, profit, price, time
         );
         first = false;
      }
   }
   json_deals += "]";
   
    // Prepare WebRequest
    string payload = StringFormat("{\"token\":\"%s\",\"account\":%lld,\"deals\":%s}", InpUserToken, AccountInfoInteger(ACCOUNT_LOGIN), json_deals);
    string headers = "Content-Type: application/json";
    
    char postData[];
    char result[];
    string recvHeaders;
    
    StringToCharArray(payload, postData, 0, WHOLE_ARRAY, CP_UTF8);
    
    // Send to your backend
    int res = WebRequest("POST", InpWebhookURL, headers, 5000, postData, result, recvHeaders);
   
    if(res == 200) {
       Print("[OK] Successfully synced ", deals_total, " trades (Account: ", AccountInfoInteger(ACCOUNT_LOGIN), ")");
    } else {
       Print("[ERROR] Sync failed - Error code: ", res, " | Webhook: ", InpWebhookURL, " | Account: ", AccountInfoInteger(ACCOUNT_LOGIN));
    }
}