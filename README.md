# information-retrieval-project-
**Velouria**: Personalized Search Engine for the Fashion Industry
Project Overview: Velouria is a personalized search engine designed specifically for clothing, enabling users to efficiently search and retrieve clothing-related information from various clothing websites. This project involves techniques such as indexing, retrieving, filtering, clustering, and presenting both textual and multimedia data sourced from digital archives, web content, and multimedia systems. By leveraging these techniques, Velouria aims to create a tailored experience for fashion enthusiasts, allowing them to discover clothing items with greater precision and relevance.


Data Indexing and Retrieval: Velouria indexes data from multiple clothing websites to facilitate fast and accurate searches. It handles diverse data formats, including text and images, ensuring that users can find products, brands, and categories with ease.
Web Scraping and Automation: The engine uses BeautifulSoup4 for web scraping, extracting product details, descriptions, prices, and images from e-commerce websites. Selenium with Chromedriver is utilized for browser automation, ensuring that dynamic content is loaded and accessible for scraping.
Filtering and Clustering: The search engine offers filtering capabilities, allowing users to refine search results based on multiple criteria such as price range, color, brand, and more. Additionally, clustering algorithms group similar items, providing users with relevant recommendations.
Presentation of Results: The project also focuses on presenting the results effectively, displaying both textual and multimedia information in an intuitive and user-friendly interface.


The tools used are the following:
Whoosh: An efficient and flexible indexing engine used for indexing and searching large amounts of data. Whoosh enables fast full-text search capabilities for the search engine.
BeautifulSoup4: A Python library for parsing HTML and XML documents. It’s used to scrape data from clothing websites, extracting necessary product details such as prices, descriptions, and images.
Selenium with Chromedriver: Used for automating web browsing and scraping dynamic content that loads with JavaScript, which is essential for modern e-commerce websites.
Flask: A lightweight Python web framework used to build the backend of the application. Flask serves as the foundation for handling web requests, routing, and user interactions.
JavaScript, HTML, and CSS: Utilized for the front-end development to ensure an engaging and responsive user interface that allows users to easily search and view products.


In order to start the system, open terminal and type "python app.py" or "python3 app.py" depending on your machine.
