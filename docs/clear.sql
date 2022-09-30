delete from sale_order where state = 'sale';
delete from sale_order_line where state = 'sale';

delete from purchase_order;
delete from purchase_order_line;

delete from stock_picking;
delete from stock_move;
delete from stock_move_line;

delete from stock_quant;
delete from stock_valuation_layer;


delete from account_partial_reconcile;
delete from account_move_line;
delete from account_move;

delete from ir_property where name = 'standard_price';
update product_template set other_purchases_count = 0;
update product_template set other_sales_count = 0;

delete from product_supplierinfo;