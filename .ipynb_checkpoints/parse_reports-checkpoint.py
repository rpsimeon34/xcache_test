import argparse
import awkward as ak
import pickle as pkl
import matplotlib.pyplot as plt
import hist

class ParsedReport:
    def __init__(self,rep):
        with open(rep,"rb") as f:
            reports_plus = pkl.load(f)
        self.reports = {}
        for dset, infos in reports_plus.items():
            if dset != "TotalTime":
                self.reports[dset] = infos
        #The total time, if available
        self.TotalTime = reports_plus.get("TotalTime",None)
        self.errors = {}
        for dset in self.reports.keys():
            self.errors[dset] = self.reports[dset][~ak.is_none(self.reports[dset].message)]

        #Calculate some aggregate metrics
        self._chunk_fail_rate()
        self._count_chunks()
        self._file_fail_rate()
        self._count_files()
        self._count_sites()
        self._count_messages()

    def print_metrics(self,sites=False):
        print("AGGREGATE INFO:\n----------------------------------------------------")
        print(f"Total number of files: {self.num_files}")
        print(f"Total file read error rate: {100*self.tot_file_fail_rate}%")
        print(f"Total number of chunks: {self.num_chunks}")
        print(f"Total chunk read error rate: {100*self.tot_chunk_fail_rate}%")
        if self.TotalTime is not None:
            print(f"Total time of test: {self.TotalTime:.2f} seconds")
        else:
            print("Total time of test unavailable for this report")
        
        print("\n========================================================\n")
        print("PER-DATASET INFO:\n----------------------------------------------------")
        for dset in self.reports.keys():
            print(f"Dataset: {dset}")
            print(f"\tNumber of files: {len(set(self.reports[dset].args[:,0]))}")
            print(f"\tFile read error rate: {100*self.file_fail_rates[dset]}%")
            print(f"\tNumber of chunks: {ak.num(self.reports[dset],axis=0)}")
            print(f"\tChunk read error rate: {100*self.chunk_fail_rates[dset]}%")
        print("\n========================================================\n")
        print("ERROR MESSAGES:\n----------------------------------------------------")
        for msg in self.messages:
            print(f"Error message: {msg}")
            print(f"\tChunks with this message: {self.messages_count[msg]}")
        if not sites:
            return
        print("\n========================================================\n")
        print("SITES INFO:\n----------------------------------------------------")
        for site in self.site_counts.keys():
            print(f"Site: {site}")
            print(f"\tNumber of files: {self.site_counts[site]}")
            print(f"\tFile read failure rate at this site: {100*self.site_error_counts[site]/self.site_counts[site]}%")

    def _chunk_fail_rate(self):
        self.chunk_fail_rates = {}
        for dset in self.reports.keys():
            self.chunk_fail_rates[dset] = ak.num(self.errors[dset],axis=0)/ak.num(self.reports[dset],axis=0)

    def _count_chunks(self):
        self.num_chunks = 0
        self.num_error_chunks = 0
        for dset in self.reports.keys():
            self.num_chunks += ak.num(self.reports[dset],axis=0)
            self.num_error_chunks += ak.num(self.errors[dset],axis=0)
        self.tot_chunk_fail_rate = self.num_error_chunks/self.num_chunks

    def _file_fail_rate(self):
        self.file_fail_rates = {}
        for dset in self.reports.keys():
            num_files = len(set(self.reports[dset].args[:,0]))
            num_error_files = len(set(self.errors[dset].args[:,0]))
            self.file_fail_rates[dset] = num_error_files/num_files

    def _count_files(self):
        self.num_files = 0
        self.num_error_files = 0
        for dset in self.reports.keys():
            self.num_files += len(set(self.reports[dset].args[:,0]))
            self.num_error_files += len(set(self.errors[dset].args[:,0]))
        self.tot_file_fail_rate = self.num_error_files/self.num_files

    def _count_sites(self):
        self.site_counts = {}
        self.site_error_counts = {}
        for dset in self.reports.keys():
            files = set(self.reports[dset].args[:,0])
            for f in files:
                file_count = ak.sum((self.reports[dset].args[:,0] == f) & (self.reports[dset].args[:,2] == "0"))
                error_file_count = ak.sum((self.errors[dset].args[:,0] == f) & (self.errors[dset].args[:,2] == "0"))
                site = f.split('/store')[0]
                self.site_counts[site] = self.site_counts.get(site,0) + file_count
                self.site_error_counts[site] = self.site_error_counts.get(site,0) + error_file_count
                

    def _count_messages(self):
        _messages_list = []
        for dset in self.errors.keys():
            _messages_list += list(set(self.errors[dset].message))
        _messages_set = set(_messages_list)
        self.messages = ak.str.trim(ak.Array(_messages_set),'\n')
        self.messages_count = {}
        for dset in self.errors.keys():
            if ak.num(self.errors[dset].message,axis=0) == 0:
                continue
            for msg in _messages_set:
                if msg[-1] == '\n':
                    msg_clean = msg[:-1]
                else:
                    msg_clean = msg
                self.messages_count[msg_clean] = self.messages_count.get(msg_clean,0) + ak.sum(self.errors[dset].message == msg)

    def sites_piechart(self,group_small=False):
        """
        If group_small, gather all sites with 0% failure and accounting for < 3% of total files into one group.
        """
        THRESHOLD = 0.03
        sites = []
        counts = []
        other = 0
        for site,count in self.site_counts.items():
            if group_small and (self.site_counts[site]/self.num_files < THRESHOLD) and (self.site_error_counts[site] == 0):
                other += self.site_counts[site]
                continue
            sites.append(site+f" ({100*self.site_error_counts[site]/self.site_counts[site]:.1f}%)")
            counts.append(count)

        if group_small:
            sites.append("Other (0%)")
            counts.append(other)

        fig,ax = plt.subplots()
        ax.set_title("Files per Site\nLabeling: Site (Failure Rate per Site)")
        ax.pie(counts,labels=sites)

    def msg_hist(self):
        messages = []
        sites = []
        for infos in self.errors.values():
            messages += list(infos.message)
            sites += list(ak.str.split_pattern(infos.args[:,0],'/store')[:,0])

        site_axis = hist.axis.StrCategory(set(sites),growth=False,name="sites")
        msg_axis = hist.axis.StrCategory(set(messages),growth=False,name="msg")
        h = hist.Hist(site_axis,msg_axis)
        h.fill(sites=sites,msg=messages)
        fig,ax = plt.subplots()
        ax.tick_params(axis='x',labelrotation=90)
        h.plot()

def main():
    parser = argparse.ArgumentParser(
        description="Report parser"
    )
    parser.add_argument("--report", type=str, default="_unset_", help="Where the report to be read is")
    parser.add_argument("--messages", action="store_true", help="Save a histogram figure of the different error messages")
    parser.add_argument("--sites", action="store_true", help="Save a pie chart showing the sites that files were drawn from")

    args = parser.parse_args()

    if args.report == "_unset_":
        print("Please indicate a report to be read with `python3 parse_reports.py --report path/to/report.pkl`")
        return
    print(f"Reading report from {args.report}")

    rep = ParsedReport(args.report)
    rep.print_metrics(sites=True)

    if args.messages:
        if rep.tot_file_fail_rate == 0.0:
            print("Unable to generate a figure of error messages, since there were no file read errors")
        else:
            output_name = args.report.split("/")[-1].strip(".pkl")+"_messages.png"
            rep.msg_hist()
            plt.savefig(output_name)
            print(f"Saved messages figure to {output_name}")
    if args.sites:
        output_name = args.report.split("/")[-1].strip(".pkl")+"_sites.png"
        rep.sites_piechart()
        plt.savefig(output_name)
        print(f"Saved sites figure to {output_name}")

if __name__ == "__main__":
    main()