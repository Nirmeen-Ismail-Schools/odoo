# Use the official Odoo 16 base image
FROM odoo:16

# Set the working directory to /mnt/extra-addons
WORKDIR /mnt/extra-addons

# Copy the contents of the local 'addons' directory to the container's 'extra-addons' directory
COPY addons/ /mnt/extra-addons/

# Copy the contents of the local 'custom-modules' directory to the container's 'extra-addons' directory
COPY custom-modules/ /mnt/extra-addons/

# Expose the Odoo port
EXPOSE 8069

# Set environment variables for database connection
ENV DB_HOST=your_remote_postgres_host
ENV DB_PORT=5432
ENV DB_USER=your_database_user
ENV DB_PASSWORD=your_database_password
ENV DB_NAME=your_database_name

COPY debian/odoo.conf /etc/odoo/odoo.conf

# Entrypoint command to start Odoo with custom addons path and database connection details
CMD ["odoo", "--addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons", "--without-demo=all", "--db_host=34.27.94.79", "--db_user=Odoo16", "--db_password='G9@?K>J~xKi^}_i_'", "--database=odoo"]
