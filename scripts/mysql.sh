# sellinfo总体走势
if [ $1 -eq 1 ];then
    mysql -uroot -e "
        use ershoufang;
        select dealdate,
               sum(cast(totalPrice as unsigned))/count(1) as totalPrice,
               sum(cast(unitPrice as unsigned))/count(1) as unitPrice,
               sum(cast(square as unsigned))/count(1) as square,
               count(1) as count 
        from sellinfo 
        where cast(square as unsigned)<2000
              and cast(years as unsigned)>2000
              and cast(dealdate as unsigned)>2015
        group by dealdate order by dealdate;
    " > data/1.csv

    /usr/local/bin/python3.8 src/draw3.py --data data/1.csv --plt_name 'ErShoufang'
fi

# sellinfo某小区走势
if [ $1 -eq 2 ];then
    community=$2
    mysql -uroot -e "
        use ershoufang;
        select dealdate, cast(totalPrice as unsigned) as totalPrice, 
            cast(unitPrice as unsigned) as unitPrice, cast(square as unsigned) as square, 1 as count
            from sellinfo 
            where 
                community like '%${community}%'  or floor like '%${community}%'
                and cast(years as unsigned)>2000
                and cast(square as unsigned)<2000
            order by unitPrice;
    " > data/2.csv
    /usr/local/bin/python3.8 src/draw3.py --data data/2.csv --plt_name "$community"
fi

# sellinfo按squre, totalPrice分档count
if [ $1 -eq 3 ];then
    mysql -uroot -e "
        use ershoufang;
        select sum(a.count) as count, a.square as square, a.totalPrice as totalPrice 
        from
        (
            select cast(square as unsigned) as square,
                cast(totalPrice as unsigned) as totalPrice,
                1 as count
            from sellinfo 
            where cast(square as unsigned)<2000
                  and cast(square as unsigned)>50
        )a
        group by square, totalPrice
    " 
fi

# 按价格区间
if [ $1 -eq 4 ];then
    mysql -uroot -e "
        use ershoufang;
        select * 
        from
        houseinfo
        where cast(totalPrice as unsigned) > 10000
    " 
fi


