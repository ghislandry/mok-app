function cropImage(imageBox, inputElem, cropBtn) {
	    const input = document.getElementById('id_image')
	    const img_data = input.files[0]
        const crop_btn = document.getElementById('crop-btn')
        console.log(img_data)
        // createObjectURL() static method creates a DOMString containing a URL representing the object given in the parameter.
	    // The new object URL represents the specified File object or Blob object.
	    const url = URL.createObjectURL(img_data)
	    console.log(url)
        imagebox = document.getElementById('image-box')
	    // Creating a image tag inside imagebox which will hold the cropping view image(uploaded file) to it using the url created before.
	     imagebox.innerHTML = `<img src="${url}" id="image" style="width:100%;">`

	    // Storing that cropping view image in a variable
	    const image = document.getElementById('image')

	    // Displaying the image box
	    document.getElementById('image-box').style.display = 'block'
	    // Displaying the Crop buttton
	    document.getElementById('crop-btn').style.display = 'block'
	    // Hiding the Post button
	    document.getElementById('confirm-btn').style.display = 'none'
        console.log('here we are!!!')
        // Creating a croper object with the cropping view image
	    // The new Cropper() method will do all the magic and diplay the cropping view and adding cropping functionality on the website
	    // For more settings, check out their official documentation at https://github.com/fengyuanchen/cropperjs
	    const cropper = new Cropper(image, {
	        autoCropArea: 0.1,
	        viewMode: 1,
	        scalable: false,
	        zoomable: false,
	        movable: false,
	        minCropBoxWidth: 150,
	        minCropBoxHeight: 150,
	    })
	    // When crop button is clicked this event will get triggered
      console.log('Starting copping !!!')
	  crop_btn.addEventListener('click', ()=>{
	    // This method coverts the selected cropped image on the cropper canvas into a blob object
	    cropper.getCroppedCanvas().toBlob((blob)=>{

	      // Gets the original image data
	      let fileInputElement = document.getElementById('id_image');
	      // Make a new cropped image file using that blob object, image_data.name will make the new file name same as original image
	      let file = new File([blob], img_data.name,{type:"image/*", lastModified:new Date().getTime()});
	      // Create a new container
	      let container = new DataTransfer();
	      // Add the cropped image file to the container
	      container.items.add(file);
	      // Replace the original image file with the new cropped image file
	      fileInputElement.files = container.files;
          console.log('Cropping !!!!!!')
	      // Hide the cropper box
	      document.getElementById('image-box').style.display = 'none'
	      // Hide the crop button
	      document.getElementById('crop-btn').style.display = 'none'
	      // Display the Post button
	      document.getElementById('confirm-btn').style.display = 'block'
	      document.getElementById('file_name').value = img_data.name
	      });
	    });
    }