This is now deprecated in favor of ColorChain



blockreader
===========

Block Chain Explorer &amp; Visualizer

To get started

download blocks from the internet

	type
		saveblocks(starting_block_number, end_block_number)
	
			the first block is # 0


	


process blocks

	type blocks(starting_block_number,  end_block_number, TRUE)  //True means find blocks locally, False means it looks on the internet for each block


		note that your starting_block_number should be EQUAL TO the variable LASTBLOCK (which really should be named NEXTBLOCK)




	All process BTC information is stored in two parallel lists

		address_list holds all addresses
		
		btc_list holds all their BTC assets

	Don't call these lists directly, they are too big after a few blocks.

	You can find an element in the list by using findinlist(ITEM,LIST).  This does a binary search and is very fast.





Refine list
	To clear addresses with BTC=0, type clear(n)    where n is a large number (n is the max number to clear, this may need to be called several times, I suggest n=10000)

	To check that everything is OK, type check().   This should return a number extremely close to 50.




