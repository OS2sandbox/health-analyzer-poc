# Evidence Template Project


The `selinuxRelabel: "shared"` line tells Podman to automatically manage the SELinux context of the host directory, ensuring the container has the necessary permissions to read and write files without manual configuration.

Otherwise just use: `sudo chcon -Rt container_file_t /home/jmk/Repositories/evidence-dev`


The `args` field in the manifest contains a series of commands that are run in sequence to prepare and start the development server.

The command is:
`npm install && npm run sources && npm run dev -- --host`

This single line tells the container to perform three separate actions, one after the other. It's a key part of making this setup simple and reliable. 

#### Command Breakdown

- **`npm install`**: This command downloads and installs the project's dependencies from `package.json` into the `node_modules` directory. The first time you run this, it will take some time to download everything. On subsequent runs, it will be much faster as it only installs what's missing or changed. 💡 For a more consistent and faster build, especially in CI/CD, you could use `npm ci` instead, which performs a "clean install" based strictly on the `package-lock.json` file.
- **`&&`**: This is a logical operator. It tells the shell to run the next command **only if the previous one was successful**. This ensures the dev server doesn't start before the dependencies are installed and the data sources are ready.
- **`npm run sources`**: This command is specific to the Evidence framework. It processes the raw data files in your `/sources` directory and generates the necessary files for the application to use. This step is required for the application to have data to display.
- **`npm run dev`**: This starts the Vite development server. It watches for changes in your project files and automatically reloads the application in your browser.
- **`-- --host`**: This is the most important part for networking. The first `--` is a special syntax that tells `npm` to pass all following arguments directly to the script being run (in this case, `npm run dev`). The `--host` flag then tells the Vite dev server to bind to `0.0.0.0` instead of `localhost`. This makes the server accessible from your host machine's browser, allowing you to view your project at `http://localhost:3000`.

To create a database file from a .json file (resulting data from an API query), use the following command:

`podman run --rm -it --name duckdb-importer -v "$(pwd)":/data docker.io/duckdb/duckdb -c "INSTALL json; LOAD json; CREATE OR REPLACE TABLE project_health AS SELECT * FROM read_json_auto('/data/project_health.json');"`