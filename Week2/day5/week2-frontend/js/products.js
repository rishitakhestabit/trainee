const productsContainer = document.getElementById("productsContainer");
const searchInput = document.getElementById("searchInput");
const categoryFilter = document.getElementById("categoryFilter");
const sortPrice = document.getElementById("sortPrice");

let allProducts = [];


fetch("https://dummyjson.com/products")
  .then(res => res.json())
  .then(data => {
    allProducts = data.products;
    populateCategories(allProducts);
    renderProducts(allProducts);
  });

function populateCategories(products) {
  const categories = new Set(products.map(p => p.category));
  categories.forEach(category => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categoryFilter.appendChild(option);
  });
}


function renderProducts(products) {
  productsContainer.innerHTML = "";

  products.forEach(product => {
    const card = document.createElement("div");
    card.className = "product-card";

    card.innerHTML = `
      <img src="${product.thumbnail}" alt="${product.title}">
      <h3>${product.title}</h3>
      <p>$${product.price}</p>
    `;

    productsContainer.appendChild(card);
  });
}

function applyFilters() {
  let filtered = [...allProducts];

  const searchText = searchInput.value.toLowerCase();
  const category = categoryFilter.value;
  const sortValue = sortPrice.value;


  if (searchText) {
    filtered = filtered.filter(p =>
      p.title.toLowerCase().includes(searchText)
    );
  }


  if (category !== "all") {
    filtered = filtered.filter(p => p.category === category);
  }

  if (sortValue === "high") {
    filtered.sort((a, b) => b.price - a.price);
  } else if (sortValue === "low") {
    filtered.sort((a, b) => a.price - b.price);
  }

  renderProducts(filtered);
}


searchInput.addEventListener("input", applyFilters);
categoryFilter.addEventListener("change", applyFilters);
sortPrice.addEventListener("change", applyFilters);
