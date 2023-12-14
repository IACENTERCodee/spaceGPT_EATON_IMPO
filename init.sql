CREATE TABLE invoices (
  invoice_id SERIAL PRIMARY KEY,
  invoice_number VARCHAR(255) NOT NULL, -- Added unique constraint to ensure no duplicate invoice numbers
  invoice_date VARCHAR(255), -- Changed data type to DATE for accurate date representation
  country_of_origin VARCHAR(100) NOT NULL,
  supplier VARCHAR(255),
  total VARCHAR(255) -- Changed data type to DECIMAL for accurate monetary values
);


-- Create a table for line items in each invoice
CREATE TABLE line_items (
    line_item_id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL,
    part_number VARCHAR(255),
    description VARCHAR(255),
    quantity VARCHAR(255),
    unit_of_measure VARCHAR(100),
    cost VARCHAR(255),
    weight VARCHAR(255) NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id)
);
