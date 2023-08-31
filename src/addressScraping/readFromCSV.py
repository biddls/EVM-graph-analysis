import pandas as pd
from addressScraping.contractObj import Contract
from tqdm import tqdm

class Reader:
    @staticmethod
    def readCSV(path, toDrop = {}):
        df = pd.read_csv(path, low_memory=False)
        df = df.drop(columns=toDrop)
        return df
    
    @staticmethod
    def convertToConts(
        *args, **kwargs
    ) -> set[Contract]:
        """convers dataframe to contract objects

        Args:
            df (DataFrame): dataframe object holding data to be extracted
            addressCol (str): column where the address is stored
            tagCols set[str]: holds tags to be added
            nameCol (str | None): optional Name Column

        Returns:
            set[Contract]: a set of Contract objects
        """
        numberOfParams = 3
        if len(args) != numberOfParams:
            raise TypeError("""Wrong number of parameters. """\
                            f"""Should be {numberOfParams}. """\
                            f"""Was given {len(args)}""")
        columns: set[str] = set(args[0].columns.values)
        if kwargs.get('progBar', False):
            itter = tqdm(args[0].iterrows(), total=len(args[0]))
        else:
            itter = args[0].iterrows()
        contracts = {Reader.processRow(row, columns, *args[1:]) for _, row in itter}
        return contracts
    
    @staticmethod
    def processRow(
        _row: pd.Series,
        cols: set[str],
        addressCol: str,
        tagCols: set[str],
    ) -> Contract:
        address = _row[addressCol]
        try:
            tags = {_row[tag] for tag in tagCols}
        except KeyError:
            raise ValueError(
                f"""all columns referenced in {f'{tagCols=}'.split('=')[0]} """\
                f"""should be in {f'{_row=}'.split('=')[0]}.\n"""\
                f"""{cols = }\n"""\
                f"""{tagCols = }""")

        return Contract(tags, address, 'forceSet')
    
    @staticmethod
    def main() -> set[Contract]:
        # processes ERC20's
        path = "data\\erc20Addrs.csv"
        print(f"reading {path}")
        df = Reader.readCSV(path,
                            {"blockchain"})
        # print(df.head())
        erc20s = Reader.convertToConts(
            df,
            "contract_address",
            {'symbol'},
            progBar = True)
        print(f"{len(erc20s)} ERC20 contracts processed")

        # processes NFTs
        path = "data\\nftAddrs.csv"
        print(f"reading {path}")
        df = Reader.readCSV(path,
                            {"blockchain"})
        # print(df.head())
        nfts = Reader.convertToConts(
            df,
            "contract_address",
            {'name', 'symbol', 'standard'},
            progBar = True)
        print(f"{len(nfts)} NFT contracts found")
        conts = nfts | erc20s
        print(f"{len(conts)} total contracts found")
        return conts

if __name__ == "__main__":
    Reader.main()