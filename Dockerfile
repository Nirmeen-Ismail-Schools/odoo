# Use an official Odoo image as a base
FROM odoo:16.0

# Set the working directory in the container
WORKDIR /usr/src/odoo

# Copy the custom modules to the addons directory
COPY addons/ addons/
COPY custom-modules/ custom-modules/

# Expose the Odoo port
EXPOSE 8069

# Start Odoo
CMD ["odoo", "--addons-path=addons/,custom-modules/", "-d", "odoo", "-u", "ashtar-sales"]

