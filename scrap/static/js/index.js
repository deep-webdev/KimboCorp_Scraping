// import { getColumnList, getProductsList } from "./data.js";

// //place the navbar
// // const navBar = document.querySelector(".navbar");
// // fetch("/templates/navbar.html")
// //   .then((res) => res.text())
// //   .then((data) => {
// //     navBar.innerHTML = data;
// //   });

// //place the footer
// // const footer = document.querySelector(".footer");
// // fetch("../../templates/footer.html")
// //   .then((res) => res.text())
// //   .then((data) => {
// //     footer.innerHTML = data;
// //   });

// //get the product list
// const productList = getProductsList();
// console.log(productList);
// //get the column list
// const columnList = getColumnList();

// //column list
// let tableHeader = document.getElementById("tableHeader");
// let columnData = "";
// for (var i = 0; i < columnList.length; i++) {
//   columnData += `<th>${columnList[i].name}</th>`;
// }
// tableHeader.innerHTML = columnData;

// //row list
// let tableBody = document.getElementById("tableBody");
// let data = "";
// for (var i = 0; i < productList.length; i++) {
//   data += `<tr id=${productList[i].productId}>
//   <td>${productList[i].productId}</td>
//   <td>${productList[i].productName}</td>
//   <td>${productList[i].price}</td>
//   <td>${productList[i].weight}</td>
//   <td>${productList[i].manufacturer}</td>
//   <td>${productList[i].supplierName}</td>
//   <td>${productList[i].supplierCountry}</td>
//   <td style="width: 10%"><a href="${productList[i].productURL}" target="blank" class="productURL" />${productList[i].productURL}</td>
//   <td>${productList[i].purity}</td>
//   </tr>`;
// }
// console.log("DATA", data);
// tableBody.innerHTML = data;
